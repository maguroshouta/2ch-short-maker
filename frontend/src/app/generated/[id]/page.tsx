import DownloadButton from "@/components/download-button";
import ShareButton from "@/components/share-button";
import VideoSwiper from "@/components/thumbnail-swiper";

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
