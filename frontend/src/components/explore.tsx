"use client";

import ThumbnailCard from "@/components/thumbnail-card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useState } from "react";

export default function Explore(props: { videos: Videos }) {
	const [videos, setVideos] = useState<Video[]>(props.videos.generated);
	const [isNext, setIsNext] = useState<boolean>(props.videos.is_next);

	const [loading, setLoading] = useState(false);

	async function viewMore() {
		const res = await fetch(
			`${process.env.NEXT_PUBLIC_API_URL}/api/videos?offset=${videos.length}`,
			{
				cache: "no-store",
			},
		);
		const newVideos: Videos = await res.json();
		setIsNext(newVideos.is_next);
		setVideos([...videos, ...newVideos.generated]);
	}

	return (
		<>
			<div className="flex flex-col gap-4 justify-center md:flex-row md:flex-wrap">
				{videos.map((video) => (
					<ThumbnailCard key={video.id} video={video} />
				))}
			</div>
			{isNext && (
				<Button disabled={loading} onClick={viewMore} className="mt-4">
					もっと見る
					{loading && <Loader2 className="animate-spin" />}
				</Button>
			)}
		</>
	);
}
