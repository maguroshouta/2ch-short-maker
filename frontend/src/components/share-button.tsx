"use client";

import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Share2 } from "lucide-react";
import { useState } from "react";

export default function ShareButton({ video }: { video: Video }) {
	const [isOpen, setIsOpen] = useState(false);

	return (
		<>
			<span
				onClick={() => setIsOpen(true)}
				className="cursor-pointer border bg-white rounded-full"
			>
				<Share2 className="pr-1 py-2" size={48} color="#000" />
			</span>
			<Dialog open={isOpen} onOpenChange={setIsOpen}>
				<DialogContent className="sm:max-w-md">
					<DialogHeader>
						<DialogTitle>共有</DialogTitle>
						<DialogDescription>
							このリンクをコピーして共有することができます
						</DialogDescription>
					</DialogHeader>
					<div className="flex items-center space-x-2">
						<div className="grid flex-1 gap-2">
							<Label htmlFor="link" className="sr-only">
								Link
							</Label>
							<Input
								defaultValue={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}`}
								readOnly
							/>
						</div>
					</div>
					<DialogFooter className="sm:justify-start">
						<DialogClose asChild>
							<Button className="w-full" type="button" variant="secondary">
								閉じる
							</Button>
						</DialogClose>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</>
	);
}
