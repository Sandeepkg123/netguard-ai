import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Audit from "./pages/Audit";
import Report from "./pages/Report";
import SBMViewer from "./pages/SBMViewer";
import Frameworks from "./pages/Frameworks";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/audit/:fileId" element={<Audit />} />
          <Route path="/report/:auditId" element={<Report />} />
          <Route path="/sbm/:fileId" element={<SBMViewer />} />
          <Route path="/frameworks" element={<Frameworks />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;