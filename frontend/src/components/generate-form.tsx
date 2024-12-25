"use client";

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

const formSchema = z.object({
	prompt: z
		.string({ message: "入力してください" })
		.max(50, { message: "50文字以内で入力してください" }),
});

export default function GeneratePage() {
	const router = useRouter();

	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			prompt: "",
		},
	});

	async function onSubmit(values: z.infer<typeof formSchema>) {
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
		const json: Video = await res.json();
		router.push(`/generated/${json.id}`);
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
								<Input placeholder="お寿司" {...field} />
							</FormControl>
							<FormMessage />
						</FormItem>
					)}
				/>
				<Button type="submit">生成する</Button>
			</form>
		</Form>
	);
}
