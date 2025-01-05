"use client";

import VideoCard from "@/components/thumbnail-card";
import Marquee from "react-fast-marquee";

export default function ThumbnailSwiper({ videos }: { videos: Videos }) {
	return (
		<Marquee speed={100} autoFill={true} pauseOnHover={true}>
			{videos.generated.map((video) => (
				<VideoCard key={video.id} video={video} />
			))}
		</Marquee>
	);
}
