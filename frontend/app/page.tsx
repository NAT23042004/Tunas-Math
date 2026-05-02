export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4 text-center">
          Toán Socratic
        </h1>
        <p className="text-center text-gray-600 mb-8">
          AI-powered Vietnamese math tutor for Grade 12 students
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <h2 className="font-bold mb-2">Socratic Method</h2>
            <p className="text-sm">Learn by asking questions, not getting answers</p>
          </div>
          <div className="border rounded-lg p-4">
            <h2 className="font-bold mb-2">3D Geometry</h2>
            <p className="text-sm">Interactive visualization for spatial problems</p>
          </div>
          <div className="border rounded-lg p-4">
            <h2 className="font-bold mb-2">Progress Tracking</h2>
            <p className="text-sm">Track your mastery across topics</p>
          </div>
        </div>
      </div>
    </main>
  )
}
