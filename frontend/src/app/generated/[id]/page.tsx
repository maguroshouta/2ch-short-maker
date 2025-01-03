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
		<div className="my-8 flex flex-col items-center gap-4">
			<div className="relative flex gap-2">
				<video className="w-64 rounded-lg md:w-96" controls loop>
					<source
						src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}`}
					/>
				</video>
				<div className="absolute bottom-2 -right-16 flex flex-col gap-4">
					<DownloadButton video={video} />
					<ShareButton video={video} />
				</div>
			</div>
			<h2 className="mt-4 text-2xl font-bold">最近生成された動画</h2>
			<div className="w-full">
				<VideoSwiper videos={videos} />
			</div>
		</div>
	);
}
