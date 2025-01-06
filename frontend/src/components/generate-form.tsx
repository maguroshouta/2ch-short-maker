"use client";

import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import Script from "next/script";

export default function GeneratePage() {
	const { toast } = useToast();
	const router = useRouter();

	const [loading, setLoading] = useState(false);

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		const formData = new FormData(e.currentTarget);
		setLoading(true);
		toast({
			title: "生成中...",
			description: "しばらくお待ちください。",
		});
		try {
			const res = await fetch(
				`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generate`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						prompt: formData.get("prompt"),
						token: formData.get("cf-turnstile-response"),
					}),
				},
			);

			if (res.status === 429) {
				toast({
					variant: "destructive",
					title: "リクエストが多すぎます。",
					description: "しばらく時間をおいてお試しください。",
				});
				setLoading(false);
				return;
			}

			if (res.status === 422) {
				toast({
					variant: "destructive",
					title: "入力エラーが発生しました。",
					description: "1文字以上50文字以内で入力してください。",
				});
				setLoading(false);
			}

			if (!res.ok) {
				toast({
					variant: "destructive",
					title: "エラーが発生しました。",
					description: "もう一度お試しください。",
				});
				setLoading(false);
				return;
			}

			const json: Video = await res.json();

			router.push(`/generated/${json.id}`);
		} catch (err) {
			toast({
				variant: "destructive",
				title: "不明なエラーが発生しました。",
				description: "もう一度お試しください。",
			});
		}
	}

	return (
		<form onSubmit={handleSubmit} className="flex gap-2">
			<Input name="prompt" placeholder="お寿司" required />
			<Script
				src="https://challenges.cloudflare.com/turnstile/v0/api.js"
				async
				defer
			/>
			<div
				className="cf-turnstile hidden"
				data-sitekey={process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY}
			/>
			<Button disabled={loading} type="submit">
				{loading ? (
					<>
						<Loader2 className="animate-spin" />
						生成中...
					</>
				) : (
					<>生成する</>
				)}
			</Button>
		</form>
	);
}
