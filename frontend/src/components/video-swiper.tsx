"use client";

import VideoCard from "@/components/video-card";
import Marquee from "react-fast-marquee";

export default function VideoSwiper({ videos }: { videos: Video[] }) {
	return (
		<Marquee speed={100} autoFill={true} pauseOnHover={true}>
			{videos.map((video) => (
				<VideoCard key={video.id} video={video} />
			))}
		</Marquee>
	);
}
