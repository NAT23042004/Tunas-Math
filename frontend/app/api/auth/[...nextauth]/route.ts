import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import type { Session } from "next-auth"
import type { JWT } from "next-auth/jwt"

declare module "next-auth" {
  interface Session {
    user: {
      name?: string | null
      email?: string | null
      image?: string | null
      id?: string
    }
  }
}

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user && token.backendUserId) {
        session.user.id = token.backendUserId as string
        console.log('Session callback: set user.id to', token.backendUserId)
      } else {
        console.log('Session callback: backendUserId not found in token', token)
      }
      return session
    },
    async jwt({ token, user, account }) {
      if (account && user?.email) {
        try {
          console.log('JWT callback: creating/getting user in backend', user.email)
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
          const response = await fetch(`${apiUrl}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: user.email,
              name: user.name || '',
            }),
          })
          if (response.ok) {
            const backendUser = await response.json()
            token.backendUserId = backendUser.id
            console.log('JWT callback: stored backendUserId', backendUser.id)
          } else {
            console.error('JWT callback: failed to create/get user', response.status)
          }
        } catch (error) {
          console.error('JWT callback: error creating/getting user:', error)
        }
      }
      return token
    },
  },
})

export { handler as GET, handler as POST }
