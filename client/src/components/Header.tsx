import { 
  Upload, 
  User, 
  Menu,
  X,
  Database,
  LogOut,
  Settings,
  Shield,
  ChevronDown
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  currentUser: string;
  onLogout: () => void;
  onUploadMore: () => void;
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  showUploadPage?: boolean;
}

export const Header = ({ 
  currentUser, 
  onLogout, 
  onUploadMore, 
  onToggleSidebar,
  sidebarOpen,
  showUploadPage = false
}: HeaderProps) => {
  const navigate = useNavigate();
  const userInitials = currentUser
    .split(' ')
    .map(name => name.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2);

  const isLoggedIn = currentUser.trim() !== "";

  return (
    <header className="h-14 md:h-16 bg-primary border-b border-primary-light shadow-primary sticky top-0 z-[60]">
      <div className="h-full px-4 md:px-6 flex items-center justify-between">
        {/* Left Side - Logo Only */}
        <div className="flex items-center gap-2 md:gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleSidebar}
            className="text-primary-foreground hover:bg-primary-light md:hidden"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>

          {/* SafetyConnect Logo Only */}
          <div className="flex items-center">
            <img
              src="/SafetyConnect_logo.png"
              alt="SafetyConnect"
              className="h-6 md:h-7 w-auto object-contain"
              onError={(e) => {
                // Fallback if logo not found
                const target = e.currentTarget as HTMLImageElement;
                target.style.display = 'none';
                const fallback = target.nextElementSibling as HTMLElement;
                if (fallback) fallback.style.display = 'flex';
              }}
            />
            {/* Fallback if logo fails to load */}
            <div className="h-6 md:h-7 w-12 md:w-14 bg-primary-foreground rounded-lg flex items-center justify-center text-primary font-bold text-xs md:text-sm hidden">
              SC
            </div>
          </div>
        </div>

        {/* Right Side - Always show user icon, but conditionally show other elements */}
        <div className="flex items-center gap-2 md:gap-4">
          {/* Only show Data Health and Upload buttons if logged in and not on upload page */}
          {isLoggedIn && !showUploadPage && (
            <>
              {/* Data Health Icon */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/data-health")}
                className="text-primary-foreground hover:bg-primary-light border border-primary-foreground/20 w-8 h-8 md:w-9 md:h-9 p-0"
                title="LLM-Enhanced Data Health"
              >
                <Database className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={onUploadMore}
                className="text-primary-foreground hover:bg-primary-light border border-primary-foreground/20 text-xs md:text-sm"
              >
                <Upload className="h-3 w-3 md:h-4 md:w-4 mr-1 md:mr-2" />
                <span className="hidden sm:inline">Upload</span>
              </Button>
            </>
          )}
          
          {/* Enhanced User Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-8 w-8 md:h-9 md:w-9 rounded-full border border-primary-foreground/20 hover:bg-primary-light transition-all duration-200 group"
              >
                <Avatar className="h-8 w-8 md:h-9 md:w-9">
                  <AvatarFallback className="bg-primary-light text-primary-foreground group-hover:bg-primary-lighter transition-colors flex items-center justify-center">
                    {isLoggedIn ? (
                      userInitials ? (
                        <span className="text-xs md:text-sm font-medium">{userInitials}</span>
                      ) : (
                        <User className="h-4 w-4 md:h-5 md:w-5" />
                      )
                    ) : (
                      <User className="h-4 w-4 md:h-5 md:w-5" />
                    )}
                  </AvatarFallback>
                </Avatar>
                <ChevronDown className="absolute -bottom-1 -right-1 h-3 w-3 text-primary-foreground/70 bg-primary rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              className="w-64 z-[70] mt-2" 
              align="end" 
              forceMount
              sideOffset={8}
            >
              {isLoggedIn ? (
                <>
                  <DropdownMenuLabel className="font-normal p-4">
                    <div className="flex flex-col space-y-3">
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-primary/10 text-primary font-semibold flex items-center justify-center">
                            {userInitials ? (
                              <span className="text-sm font-semibold">{userInitials}</span>
                            ) : (
                              <User className="h-5 w-5" />
                            )}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold leading-none text-foreground truncate">
                            {currentUser}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            SafetyConnect User
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="secondary" className="text-xs bg-primary/10 text-primary border-primary/20">
                          <Shield className="h-3 w-3 mr-1" />
                          Safety Head
                        </Badge>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="p-3 cursor-pointer hover:bg-accent/50 transition-colors">
                    <User className="mr-3 h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">Profile</span>
                      <span className="text-xs text-muted-foreground">View your profile</span>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 cursor-pointer hover:bg-accent/50 transition-colors">
                    <Settings className="mr-3 h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">Settings</span>
                      <span className="text-xs text-muted-foreground">Manage your preferences</span>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={onLogout} 
                    className="p-3 cursor-pointer hover:bg-destructive/10 text-destructive hover:text-destructive transition-colors"
                  >
                    <LogOut className="mr-3 h-4 w-4" />
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">Sign out</span>
                      <span className="text-xs text-muted-foreground">Log out of your account</span>
                    </div>
                  </DropdownMenuItem>
                </>
              ) : (
                <>
                  <DropdownMenuLabel className="font-normal p-4">
                    <div className="flex flex-col space-y-3">
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback className="bg-muted text-muted-foreground font-semibold flex items-center justify-center">
                            <User className="h-5 w-5" />
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold leading-none text-foreground">
                            Guest User
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Not signed in
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          Limited Access
                        </Badge>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem disabled className="p-3 cursor-not-allowed opacity-50">
                    <User className="mr-3 h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">Sign in required</span>
                      <span className="text-xs text-muted-foreground">Please sign in to access features</span>
                    </div>
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};