import Link from 'next/link';

interface EmptyStateProps {
  title: string;
  message: string;
  href?: string;
  ctaLabel?: string;
}

export default function EmptyState({ title, message, href, ctaLabel }: EmptyStateProps) {
  const content = (
    <div className="w-full max-w-xl rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-500">{message}</p>
      {href && ctaLabel ? (
        <span className="mt-5 inline-flex rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white">
          {ctaLabel}
        </span>
      ) : null}
    </div>
  );

  if (href && ctaLabel) {
    return <Link href={href}>{content}</Link>;
  }

  return content;
}
