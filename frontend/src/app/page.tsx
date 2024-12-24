import { Button } from "@/components/ui/button";
import VideoSwiper from "@/components/video-swiper";

export default async function Home() {
	const res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos/recent`,
	);
	const videos: Video[] = await res.json();

	return (
		<main className="mt-16 w-full flex flex-col items-center gap-4">
			<h1 className="text-4xl font-bold">2ch ショートメーカー</h1>
			<p className="text-xl">AIで量産型のショートを生成します</p>
			<div className="flex flex-col gap-4 md:flex-row">
				<Button size="lg">今すぐ生成する</Button>
				<Button size="lg" variant="outline">
					生成されたものを見る
				</Button>
			</div>
			<h2 className="text-2xl mt-8 font-bold">最近生成された動画</h2>
			<div className="w-full">
				<VideoSwiper videos={videos} />
			</div>
		</main>
	);
}
