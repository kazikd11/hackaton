import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { OpportunityPage } from "./routes/OpportunityPage";
import { OverviewPage } from "./routes/OverviewPage";
import { ProcessPage } from "./routes/ProcessPage";
import { WorkflowPage } from "./routes/WorkflowPage";

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/processes/:id" element={<ProcessPage />} />
          <Route path="/opportunities/:id" element={<OpportunityPage />} />
          <Route path="/workflow/:id" element={<WorkflowPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
