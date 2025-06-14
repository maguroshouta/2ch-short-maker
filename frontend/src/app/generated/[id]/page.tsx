import DownloadButton from "@/components/download-button";
import ShareButton from "@/components/share-button";
import VideoSwiper from "@/components/thumbnail-swiper";
import type { Metadata } from "next";

export default async function Page({
	params,
}: {
	params: Promise<{ id: string }>;
}) {
	const id = (await params).id;

	const video_res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${id}`,
		{
			cache: "no-cache",
		},
	);

	const video: Video = await video_res.json();

	const recent_res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos`,
		{
			cache: "no-cache",
		},
	);

	const videos: Videos = await recent_res.json();

	if (!video_res.ok) {
		return (
			<div className="my-8 flex flex-col items-center gap-4">
				<div className="flex flex-col items-center gap-2">
					<h1 className="text-4xl font-bold">404 Not Found</h1>
					<p className="text-2xl">動画が見つかりません</p>
				</div>
				<h2 className="mt-4 text-2xl font-bold">最近生成された動画</h2>
				<div className="w-full">
					<VideoSwiper videos={videos} />
				</div>
			</div>
		);
	}

	return (
		<div className="my-4 flex flex-col items-center gap-4">
			<div className="relative flex flex-col">
				<p>プロンプト</p>
				<h1 className="mb-2 font-bold text-lg">{video.prompt}</h1>
				<video className="w-72 rounded-lg md:w-96" controls loop>
					<source
						src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${video.id}.mp4`}
					/>
				</video>
				<div className="flex gap-4 mt-2">
					<DownloadButton video={video} />
					<ShareButton video={video} />
				</div>
			</div>
			<h2 className="mt-2 text-2xl font-bold">最近生成された動画</h2>
			<div className="w-full">
				<VideoSwiper videos={videos} />
			</div>
		</div>
	);
}

export async function generateMetadata({
	params,
}: { params: { id: string } }): Promise<Metadata> {
	const id = params.id;
	const res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${id}`,
		{ cache: "no-cache" },
	);
	if (!res.ok) {
		return {
			title: "動画が見つかりません | 2chショートメーカー",
			description: "指定された動画は存在しません。",
		};
	}
	const video: Video = await res.json();
	const baseUrl = "https://2ch-maker.yakimaguro.com";
	return {
		title: `2chショートメーカー | ${video.prompt}`,
		description: video.prompt,
		openGraph: {
			title: `2chショートメーカー | ${video.prompt}`,
			description: video.prompt,
			url: `${baseUrl}/generated/${video.id}`,
			siteName: "2ch ショートメーカー",
			images: [
				{
					url: `${baseUrl}/generated/${video.id}.jpg`,
					width: 1080,
					height: 1920,
					alt: "2ch ショートメーカーのOGP画像",
				},
			],
			locale: "ja_JP",
			type: "video.other",
		},
		alternates: {
			canonical: `${baseUrl}/generated/${video.id}`,
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
		keywords: ["2ch", "ショート動画", "AI動画生成", "動画メーカー", "自動生成"],
	};
}
