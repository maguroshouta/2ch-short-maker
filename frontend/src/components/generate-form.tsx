"use client";

import { useToast } from "@/hooks/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
	prompt: z
		.string({ message: "入力してください" })
		.max(50, { message: "50文字以内で入力してください" }),
});

export default function GeneratePage() {
	const { toast } = useToast();
	const router = useRouter();

	const [loading, setLoading] = useState(false);

	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			prompt: "",
		},
	});

	async function onSubmit(values: z.infer<typeof formSchema>) {
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
					body: JSON.stringify(values),
				},
			);

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
		<Form {...form}>
			<form onSubmit={form.handleSubmit(onSubmit)} className="flex gap-2">
				<FormField
					control={form.control}
					name="prompt"
					render={({ field }) => (
						<FormItem>
							<FormControl>
								<Input placeholder="お寿司" {...field} required />
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
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
		</Form>
	);
}
