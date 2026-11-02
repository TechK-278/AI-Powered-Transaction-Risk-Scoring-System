import AppHeader from "./components/layout/AppHeader.jsx";
import EvaluationPage from "./pages/EvaluationPage.jsx";

export default function App() {
  return (
    <>
      <AppHeader />
      <main className="mx-auto max-w-7xl px-4 py-6">
        <h1 className="mb-4 text-lg font-semibold">Evaluate a transaction</h1>
        <EvaluationPage />
      </main>
    </>
  );
}
