import { LayoutDashboard, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  currentView?: 'main' | 'ai-dashboard';
  onSwitchToMain?: () => void;
  onOpenAIDashboard?: () => void;
}

export const Sidebar = ({ isOpen, currentView = 'main', onSwitchToMain, onOpenAIDashboard }: SidebarProps) => {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" />
      )}
      
      {/* Sidebar */}
      <aside 
        className={cn(
          "fixed left-0 top-14 md:top-16 min-h-[calc(100vh-3.5rem)] md:min-h-[calc(100vh-4rem)] bg-card border-r border-border shadow-card transition-transform duration-300 z-50 md:relative md:top-0 md:min-h-full md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
          "w-40 md:w-48"
        )}
      >
        <div className="p-3 md:p-4 space-y-2 h-full">
          {onSwitchToMain && (
            <Button
              variant="ghost"
              onClick={onSwitchToMain}
              className={cn(
                "w-full h-10 md:h-12 justify-start gap-2 md:gap-3 text-sm md:text-base",
                currentView === 'main' 
                  ? "bg-primary text-primary-foreground hover:bg-primary-light" 
                  : "hover:bg-gray-100"
              )}
            >
              <LayoutDashboard className="h-4 w-4 md:h-5 md:w-5" />
              <span className="font-medium">Dashboard</span>
            </Button>
          )}
          
          {onOpenAIDashboard && (
            <Button
              variant="ghost"
              onClick={onOpenAIDashboard}
              className={cn(
                "w-full h-10 md:h-12 justify-start gap-2 md:gap-3 text-sm md:text-base",
                currentView === 'ai-dashboard' 
                  ? "bg-primary text-primary-foreground hover:bg-primary-light" 
                  : "hover:bg-gray-100"
              )}
            >
              <BarChart3 className="h-4 w-4 md:h-5 md:w-5" />
              <span className="font-medium">AI Dashboard</span>
            </Button>
          )}
          
          {!onSwitchToMain && !onOpenAIDashboard && (
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground">Upload data to access dashboards</p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};