import NextAuth from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      userId?: string;
      accessToken?: string;
      role?: 'student' | 'admin';
    } & NonNullable<Session['user']>;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    userId?: string;
    accessToken?: string;
    role?: 'student' | 'admin';
  }
}
