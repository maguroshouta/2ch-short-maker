import GenerateForm from "@/components/generate-form";
import VideoSwiper from "@/components/thumbnail-swiper";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default async function Home() {
	const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/videos`, {
		cache: "no-store",
	});
	const videos: Videos = await res.json();

	return (
		<main className="my-16 w-full flex flex-col items-center gap-4">
			<h1 className="text-3xl font-bold md:text-4xl">2ch ショートメーカー</h1>
			<p className="mb-2 md:text-xl">AIで量産型のショートを生成します</p>
			<GenerateForm />
			<Link href="/explore">
				<Button variant="outline">生成された動画をもっと見る</Button>
			</Link>
			<h2 className="text-2xl font-bold">最近生成された動画</h2>
			<div className="w-full">
				<VideoSwiper videos={videos} />
			</div>
		</main>
	);
}
