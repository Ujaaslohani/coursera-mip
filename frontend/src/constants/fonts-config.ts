import { Inter, Sora } from 'next/font/google';

export const inter = Inter({
  subsets: ["latin"],
  weight: ['400', '500', '700'],
  variable: "--font-body"
});

export const sora = Sora({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-heading",
});