"use client";

import {zodResolver} from "@hookform/resolvers/zod";
import {AlertCircle, ArrowRight, Eye, EyeOff, LoaderCircle} from "lucide-react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {toast} from "sonner";
import {z} from "zod";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {authFetch} from "@/lib/api";

const schema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});
type Values = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: {errors, isSubmitting},
  } = useForm<Values>({resolver: zodResolver(schema)});

  const submit = handleSubmit(async (values) => {
    setFormError(null);
    try {
      await authFetch("/login", values);
      router.replace("/projects");
      router.refresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to sign in";
      setFormError(message);
      toast.error(message);
    }
  });

  return (
    <>
      <p className="inline-flex items-center gap-2 rounded-full border border-[#e85d9e]/25 bg-[#e85d9e]/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-[#f5b5d4]">
        Welcome back
      </p>
      <h1 className="mt-5 text-[34px] font-semibold leading-[1.05] tracking-[-0.02em] text-[#f5f1ea]">
        Sign in to CCSR
      </h1>
      <p className="mt-3 text-[15px] leading-6 text-[#b8b0a3]">
        Access your research projects, source artifacts, retrieval traces, and
        reproducible experiment workspace.
      </p>

      <form className="mt-8 space-y-5" onSubmit={submit} noValidate>
        <div>
          <label
            className="mb-2 block text-sm font-semibold text-[#f5f1ea]"
            htmlFor="email"
          >
            Email address
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? "email-error" : undefined}
            className="h-12 rounded-2xl border-[#2a2a2a] bg-[#161616] px-4 text-[15px] text-[#f5f1ea] shadow-[inset_0_1px_0_rgba(245,241,234,0.035)] placeholder:text-[#77716a] transition hover:border-[#403c36] focus:border-[#e85d9e]/70 focus:ring-[#e85d9e]/15"
            {...register("email")}
          />
          {errors.email ? (
            <span
              className="mt-2 block text-sm text-[#f2aaa5]"
              id="email-error"
            >
              {errors.email.message}
            </span>
          ) : null}
        </div>

        <div>
          <label
            className="mb-2 block text-sm font-semibold text-[#f5f1ea]"
            htmlFor="password"
          >
            Password
          </label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="Your password"
              aria-invalid={Boolean(errors.password)}
              aria-describedby={errors.password ? "password-error" : undefined}
              className="h-12 rounded-2xl border-[#2a2a2a] bg-[#161616] px-4 pr-12 text-[15px] text-[#f5f1ea] shadow-[inset_0_1px_0_rgba(245,241,234,0.035)] placeholder:text-[#77716a] transition hover:border-[#403c36] focus:border-[#8c6bdb]/75 focus:ring-[#8c6bdb]/18"
              {...register("password")}
            />
            <button
              type="button"
              className="absolute right-1.5 top-1.5 flex size-9 items-center justify-center rounded-xl text-[#b8b0a3] transition hover:bg-[#242424] hover:text-[#f5f1ea] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#8c6bdb] focus-visible:ring-offset-2 focus-visible:ring-offset-[#161616]"
              aria-label={showPassword ? "Hide password" : "Show password"}
              onClick={() => setShowPassword((value) => !value)}
            >
              {showPassword ? (
                <EyeOff className="size-4" aria-hidden="true" />
              ) : (
                <Eye className="size-4" aria-hidden="true" />
              )}
            </button>
          </div>
          {errors.password ? (
            <span
              className="mt-2 block text-sm text-[#f2aaa5]"
              id="password-error"
            >
              {errors.password.message}
            </span>
          ) : null}
        </div>

        {formError ? (
          <div
            className="flex gap-2 rounded-2xl border border-[#d76c6c]/35 bg-[#d76c6c]/10 px-3 py-2.5 text-sm leading-5 text-[#f2aaa5]"
            role="alert"
            aria-live="assertive"
          >
            <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <span>{formError}</span>
          </div>
        ) : null}

        <Button
          className="h-12 w-full rounded-2xl border border-[#f2a65a]/35 bg-[#f5f1ea] text-base font-semibold text-[#111111] shadow-[0_16px_40px_rgba(232,93,158,0.16),inset_0_1px_0_rgba(255,255,255,0.55)] transition hover:-translate-y-0.5 hover:bg-[#fff7ec] hover:shadow-[0_20px_54px_rgba(242,166,90,0.18),inset_0_1px_0_rgba(255,255,255,0.65)] active:translate-y-0 focus-visible:ring-[#e85d9e] focus-visible:ring-offset-[#080808]"
          size="lg"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <ArrowRight className="size-4" aria-hidden="true" />
          )}
          Sign in
        </Button>
      </form>

      <p className="mt-7 rounded-2xl border border-[#2a2a2a] bg-[#161616]/70 px-4 py-3 text-center text-sm text-[#b8b0a3]">
        New to CCSR?{" "}
        <Link
          className="font-semibold text-[#f5b5d4] underline-offset-4 hover:text-[#ffd0e6] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#e85d9e] focus-visible:ring-offset-2 focus-visible:ring-offset-[#111111]"
          href="/register"
        >
          Create an account
        </Link>
      </p>
    </>
  );
}
