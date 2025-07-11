"use client"

import React, { useState, useEffect } from 'react'
import { Menu, X, Home, Settings, Database, FileText, Bell, Search, Sun, Moon, ChevronDown, LogOut, User, Book, Headphones, HardDrive, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface NavigationItem {
  id: string
  label: string
  icon: React.ReactNode
  href: string
  badge?: number
}

interface AppLayoutProps {
  children?: React.ReactNode
  navigationItems?: NavigationItem[]
  appName?: string
  appLogo?: string
  userName?: string
  userAvatar?: string
  userEmail?: string
  onThemeToggle?: () => void
  isDarkMode?: boolean
}

const defaultNavigationItems: NavigationItem[] = [
  { id: 'dashboard', label: '控制面板', icon: <Home className="w-5 h-5" />, href: '/dashboard' },
  { id: 'words', label: '单词管理', icon: <Book className="w-5 h-5" />, href: '/words' },
  { id: 'audio', label: '音频管理', icon: <Headphones className="w-5 h-5" />, href: '/audio' },
  { id: 'cache', label: 'AI缓存', icon: <HardDrive className="w-5 h-5" />, href: '/cache' },
  { id: 'decks', label: '牌组管理', icon: <Package className="w-5 h-5" />, href: '/decks' },
  { id: 'dictionaries', label: '词典管理', icon: <Database className="w-5 h-5" />, href: '/dictionaries' },
  { id: 'settings', label: '系统设置', icon: <Settings className="w-5 h-5" />, href: '/settings' },
];

const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  navigationItems = defaultNavigationItems,
  appName = "Anki Packager",
  appLogo = "",
  userName = "用户",
  userAvatar = "",
  userEmail = "user@example.com",
  onThemeToggle = () => {},
  isDarkMode = false
}) => {
  const [isMobile, setIsMobile] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkScreenSize()
    window.addEventListener('resize', checkScreenSize)

    return () => window.removeEventListener('resize', checkScreenSize)
  }, [])

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-background border-r border-border">
      {/* Logo Section */}
      <div className="flex items-center gap-3 p-6 border-b border-border">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          {appLogo ? (
            <img src={appLogo} alt={appName} className="w-6 h-6" />
          ) : (
            <span className="text-primary-foreground font-bold text-sm">
              {appName.charAt(0)}
            </span>
          )}
        </div>
        <span className="font-semibold text-foreground text-lg">{appName}</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigationItems.map((item) => (
            <li key={item.id}>
              <Link
                href={item.href}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  pathname === item.href
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                {item.icon}
                <span className="flex-1">{item.label}</span>
                {item.badge !== undefined && (
                  <Badge variant="secondary" className="ml-auto">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center gap-4 px-4">
          {/* Mobile Menu Button */}
          {isMobile && (
            <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-80">
                <SidebarContent />
              </SheetContent>
            </Sheet>
          )}

          {/* Mobile Logo */}
          {isMobile && (
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-xs">
                  {appName.charAt(0)}
                </span>
              </div>
              <Link href="/" className="font-semibold text-foreground">{appName}</Link>
            </div>
          )}

          {/* Search Bar */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="搜索单词..."
                className="pl-10 bg-background"
              />
            </div>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-2">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={onThemeToggle}
              className="w-9 h-9"
            >
              {isDarkMode ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2 px-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={userAvatar} alt={userName} />
                    <AvatarFallback>
                      {userName.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden md:flex flex-col items-start">
                    <span className="text-sm font-medium text-foreground">{userName}</span>
                    <span className="text-xs text-muted-foreground">{userEmail}</span>
                  </div>
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem>
                  <User className="w-4 h-4 mr-2" />
                  个人资料
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="w-4 h-4 mr-2" />
                  设置
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive">
                  <LogOut className="w-4 h-4 mr-2" />
                  退出
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        {!isMobile && (
          <aside className="w-64 h-[calc(100vh-4rem)] sticky top-16">
            <SidebarContent />
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-4rem)]">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppLayout 