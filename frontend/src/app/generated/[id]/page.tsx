import VideoSwiper from "@/components/video-swiper";

export default async function Page({
	params,
}: {
	params: Promise<{ id: string }>;
}) {
	const id = (await params).id;

	const video_res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos/info/${id}`,
		{
			cache: "no-cache",
		},
	);
	const video: Video = await video_res.json();

	const recent_res = await fetch(
		`${process.env.NEXT_PUBLIC_API_URL}/api/videos/recent`,
		{
			cache: "no-cache",
		},
	);

	const videos: Video[] = await recent_res.json();

	return (
		<div className="my-8 flex flex-col items-center gap-4">
			<div className="flex flex-col gap-2">
				<h1 className="text-4xl">テーマ: {video.prompt}</h1>
				<video className="w-64 rounded-lg md:w-96" controls loop>
					<source
						src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}`}
					/>
				</video>
			</div>
			<h2 className="my-4 text-2xl font-bold">最近生成された動画</h2>
			<div className="w-full">
				<VideoSwiper videos={videos} />
			</div>
		</div>
	);
}
