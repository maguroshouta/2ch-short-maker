import { Toaster } from "@/components/ui/toaster";
import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";
import { ThemeProvider } from "next-themes";

const notoSansJP = Noto_Sans_JP({
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "2ch ショートメーカー",
	description: "量産型のショートを生成します",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="ja" suppressHydrationWarning>
			<body className={`${notoSansJP.className} antialiased`}>
				<ThemeProvider
					attribute="class"
					defaultTheme="system"
					enableSystem
					disableTransitionOnChange
				>
					<Header />
					{children}
					<Toaster />
				</ThemeProvider>
			</body>
		</html>
	);
}
