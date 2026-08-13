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
      <p className="inline-flex items-center gap-2 rounded-full border border-[var(--accent-soft-border)] bg-[var(--accent-soft)] px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--accent-hover)]">
        Welcome back
      </p>
      <h1 className="mt-4 text-[31px] font-semibold leading-[1.04] tracking-[-0.02em] text-[var(--ink)]">
        Sign in to CCSR
      </h1>
      <p className="mt-2.5 text-[14px] leading-6 text-[var(--ink-secondary)]">
        Access your research projects, source artifacts, retrieval traces, and
        reproducible experiment workspace.
      </p>

      <form className="mt-6 space-y-4" onSubmit={submit} noValidate>
        <div>
          <label
            className="mb-1.5 block text-[13px] font-semibold text-[var(--ink)]"
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
            className="h-11 rounded-xl border-[var(--border-strong)] bg-[var(--surface-muted)] px-4 text-[15px] text-[var(--ink)] shadow-[var(--shadow-input)] placeholder:text-[var(--ink-muted)] transition hover:border-[var(--border-strong)] focus:border-[var(--accent)] focus:ring-[var(--accent-soft)]"
            {...register("email")}
          />
          {errors.email ? (
            <span
              className="mt-2 block text-sm text-[var(--danger-soft-text)]"
              id="email-error"
            >
              {errors.email.message}
            </span>
          ) : null}
        </div>

        <div>
          <label
            className="mb-1.5 block text-[13px] font-semibold text-[var(--ink)]"
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
              className="h-11 rounded-xl border-[var(--border-strong)] bg-[var(--surface-muted)] px-4 pr-12 text-[15px] text-[var(--ink)] shadow-[var(--shadow-input)] placeholder:text-[var(--ink-muted)] transition hover:border-[var(--border-strong)] focus:border-[var(--research-violet)] focus:ring-[var(--tertiary-soft)]"
              {...register("password")}
            />
            <button
              type="button"
              className="absolute right-1 top-1 flex size-9 items-center justify-center rounded-xl text-[var(--ink-muted)] transition hover:bg-[var(--surface-hover)] hover:text-[var(--ink)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--research-violet)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-muted)]"
              aria-label={showPassword ? "Hide secret" : "Show secret"}
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
              className="mt-2 block text-sm text-[var(--danger-soft-text)]"
              id="password-error"
            >
              {errors.password.message}
            </span>
          ) : null}
        </div>

        {formError ? (
          <div
            className="flex gap-2 rounded-2xl border border-[var(--danger-soft-border)] bg-[var(--danger-soft)] px-3 py-2.5 text-sm leading-5 text-[var(--danger-soft-text)]"
            role="alert"
            aria-live="assertive"
          >
            <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <span>{formError}</span>
          </div>
        ) : null}

        <Button
          className="h-11 w-full rounded-xl border border-[var(--accent)] bg-[var(--accent)] text-[15px] font-semibold text-[var(--ink-inverse)] shadow-[var(--shadow-accent)] transition hover:-translate-y-0.5 hover:bg-[var(--accent-hover)] active:translate-y-0 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-[var(--background)]"
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

      <p className="mt-5 rounded-xl border border-[var(--border-strong)] bg-[var(--surface-elevated-glass)] px-4 py-2.5 text-center text-sm text-[var(--ink-secondary)]">
        New to CCSR?{" "}
        <Link
          className="font-semibold text-[var(--accent-hover)] underline-offset-4 hover:text-[var(--accent-hover)] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface)]"
          href="/register"
        >
          Create an account
        </Link>
      </p>
    </>
  );
}
