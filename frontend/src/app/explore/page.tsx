import Explore from "@/components/explore";
import { serverApiUrl } from "@/lib/api-url";

export default async function ExplorePage() {
	const video_res = await fetch(serverApiUrl("/api/videos"), {
		cache: "no-store",
	});
	const videos: Videos = await video_res.json();

	return (
		<main className="my-4 flex flex-col justify-center items-center">
			<Explore videos={videos} />
		</main>
	);
}
