import { Route, Routes } from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import "./App.css";
import Home from "./pages/Home";
import Group from "./pages/Group";

function App() {
  return (
    <ChakraProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/groups/:groupId" element={<Group />} />
      </Routes>
    </ChakraProvider>
  );
}

export default App;
