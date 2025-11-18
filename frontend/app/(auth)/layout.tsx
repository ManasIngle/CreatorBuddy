export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-brand bg-clip-text text-transparent">
            CreatorIQ
          </h1>
          <p className="text-surface-muted mt-2 text-sm">AI Growth Intelligence for Creators</p>
        </div>
        {children}
      </div>
    </div>
  );
}