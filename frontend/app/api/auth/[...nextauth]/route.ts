import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  callbacks: {
    async signIn({ user }) {
      try {
        // Create or get user from backend
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: user.email,
            name: user.name,
            avatar_url: user.image,
          }),
        });

        if (response.ok) {
          const userData = await response.json();
          // Store user_id in user object for JWT callback
          (user as unknown as Record<string, unknown>).userId = userData.id;
          return true;
        }
        return false;
      } catch {
        return false;
      }
    },
    async jwt({ token, user }) {
      if (user) {
        const userId = (user as unknown as Record<string, unknown>).userId as string;
        token.userId = userId;
        token.accessToken = (user as unknown as Record<string, unknown>).accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as unknown as Record<string, unknown>).userId = token.userId;
        (session.user as unknown as Record<string, unknown>).accessToken = token.accessToken;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
