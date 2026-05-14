import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

const nextAuthDebug = process.env.NEXTAUTH_DEBUG === 'true';

const handler = NextAuth({
  debug: nextAuthDebug,
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  logger: {
    error(code) {
      console.error('[nextauth][error]', code);
    },
    warn(code) {
      console.warn('[nextauth][warn]', code);
    },
    debug(code) {
      if (nextAuthDebug) {
        console.debug('[nextauth][debug]', code);
      }
    },
  },
  callbacks: {
    async signIn({ user, account }) {
      try {
        const googleIdToken = account?.id_token;
        if (!googleIdToken) {
          console.error('[nextauth][error]', 'Missing Google ID token');
          return false;
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id_token: googleIdToken }),
        });

        if (!response.ok) {
          console.error('[nextauth][error]', 'Backend Google auth exchange failed', response.status);
          return false;
        }

        const authData = await response.json();
        (user as unknown as Record<string, unknown>).userId = authData.user.id;
        (user as unknown as Record<string, unknown>).accessToken = authData.access_token;
        (user as unknown as Record<string, unknown>).role = authData.user.role;
        (user as unknown as Record<string, unknown>).image = authData.user.avatar_url ?? user.image;
        return true;
      } catch (error) {
        console.error('[nextauth][error]', 'Backend Google auth exchange threw', error);
        return false;
      }
    },
    async jwt({ token, user }) {
      if (user) {
        token.userId = (user as unknown as Record<string, unknown>).userId as string;
        token.accessToken = (user as unknown as Record<string, unknown>).accessToken as string;
        token.role = (user as unknown as Record<string, unknown>).role as 'student' | 'admin';
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as unknown as Record<string, unknown>).userId = token.userId as string;
        (session.user as unknown as Record<string, unknown>).accessToken = token.accessToken as string;
        (session.user as unknown as Record<string, unknown>).role = token.role as string;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
