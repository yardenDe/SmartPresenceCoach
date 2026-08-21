import { AuthProvider } from "./context/AuthContext";
import { PresenceDashboard } from "./features/presence-dashboard/PresenceDashboard";
import { useAuth } from "./hooks/useAuth";
import { Auth } from "./pages/Auth";


const AppShell = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <main className="hud-shell grid h-screen place-items-center overflow-hidden p-[2vh]">
        <div className="w-[min(94vw,680px)]">
          <Auth />
        </div>
      </main>
    );
  }

  return (
    <main className="hud-shell min-h-screen overflow-x-hidden p-2 xl:h-screen xl:overflow-hidden">
      <div className="flex min-h-0 w-full flex-col xl:h-full">
        <PresenceDashboard />
      </div>
    </main>
  );
};


export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}
