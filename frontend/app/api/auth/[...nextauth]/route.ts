import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

const nextAuthDebug = process.env.NEXTAUTH_DEBUG === 'true';
const authBridgeSecret = process.env.AUTH_BRIDGE_SECRET ?? process.env.NEXTAUTH_SECRET;

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
    async signIn({ user }) {
      try {
        if (!authBridgeSecret) {
          console.error('[nextauth][error]', 'Missing auth bridge secret');
          return false;
        }

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
          const tokenRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/token`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Auth-Bridge-Secret': authBridgeSecret,
            },
            body: JSON.stringify({ user_id: userData.id }),
          });

          if (!tokenRes.ok) {
            return false;
          }

          const tokenData = await tokenRes.json();

          // Store backend auth data for the JWT callback.
          (user as unknown as Record<string, unknown>).userId = userData.id;
          (user as unknown as Record<string, unknown>).accessToken = tokenData.access_token;
          return true;
        }
        return false;
      } catch {
        return false;
      }
    },
    async jwt({ token, user }) {
      if (user) {
        token.userId = (user as unknown as Record<string, unknown>).userId as string;
        token.accessToken = (user as unknown as Record<string, unknown>).accessToken as string;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as unknown as Record<string, unknown>).userId = token.userId as string;
        (session.user as unknown as Record<string, unknown>).accessToken = token.accessToken as string;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
