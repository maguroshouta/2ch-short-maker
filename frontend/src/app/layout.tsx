import { Toaster } from "@/components/ui/toaster";
import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";
import { ThemeProvider } from "next-themes";

const notoSansJP = Noto_Sans_JP({
	subsets: ["latin"],
});

const baseUrl = "https://2ch-maker.yakimaguro.com";

export const metadata: Metadata = {
	title: "2ch ショートメーカー",
	description: "量産型のショートを生成します",
	keywords: ["2ch", "ショート動画", "AI動画生成", "動画メーカー", "自動生成"],
	openGraph: {
		title: "2ch ショートメーカー",
		description: "量産型のショートを生成します",
		url: baseUrl,
		siteName: "2ch ショートメーカー",
		locale: "ja_JP",
		type: "website",
	},
	robots: {
		index: true,
		follow: true,
		googleBot: {
			index: true,
			follow: true,
			"max-image-preview": "large",
			"max-snippet": -1,
			"max-video-preview": -1,
		},
	},
	alternates: {
		canonical: baseUrl,
	},
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
