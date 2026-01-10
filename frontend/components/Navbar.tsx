'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from './AuthProvider';
import { signOut } from '@/lib/auth';
import { useState } from 'react';
import {
    Home, BarChart3, GitCompare, FileText, Sparkles, TrendingUp, LogOut, User, FolderOpen, Play, Menu, X
} from 'lucide-react';

const navItems = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { href: '/compare', label: 'Compare', icon: GitCompare },
    { href: '/trends', label: 'Trends', icon: TrendingUp },
    { href: '/batches', label: 'Batches', icon: FolderOpen },
];

export default function Navbar() {
    const pathname = usePathname();
    const router = useRouter();
    const { user } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    // Don't show navbar on login/signup pages
    if (pathname === '/login' || pathname === '/signup') return null;

    const handleLogout = async () => {
        try {
            await signOut();
            router.push('/login');
            // Force page reload to clear state
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const closeMobileMenu = () => setMobileMenuOpen(false);

    return (
        <>
            <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-100 shadow-sm">
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-light rounded-lg flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-lg font-bold text-gray-800">
                                Smart <span className="text-primary hidden sm:inline">Approval AI</span>
                            </span>
                        </Link>

                        {/* Desktop Navigation Items */}
                        <div className="hidden md:flex items-center gap-1">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = pathname === item.href ||
                                    (item.href !== '/' && pathname.startsWith(item.href));

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${isActive
                                            ? 'bg-primary/10 text-primary font-medium'
                                            : 'text-gray-600 hover:bg-gray-100'
                                            }`}
                                    >
                                        <Icon className="w-4 h-4" />
                                        <span className="text-sm">{item.label}</span>
                                    </Link>
                                );
                            })}

                            {/* Reports link */}
                            <Link
                                href="/reports"
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${pathname === '/reports'
                                    ? 'bg-primary/10 text-primary font-medium'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <FileText className="w-4 h-4" />
                                <span className="text-sm">Reports</span>
                            </Link>
                        </div>

                        {/* Desktop User Menu */}
                        <div className="hidden md:flex items-center gap-3">
                            {user ? (
                                <>
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <User className="w-4 h-4" />
                                        <span className="hidden lg:inline">{user.email}</span>
                                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                                            {user.role}
                                        </span>
                                    </div>
                                    <button
                                        onClick={handleLogout}
                                        className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        <span className="text-sm">Logout</span>
                                    </button>
                                </>
                            ) : (
                                <Link
                                    href="/login"
                                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                                >
                                    <Play className="w-4 h-4" />
                                    <span className="text-sm">Get Started</span>
                                </Link>
                            )}
                        </div>

                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
                            aria-label="Toggle menu"
                        >
                            {mobileMenuOpen ? (
                                <X className="w-6 h-6" />
                            ) : (
                                <Menu className="w-6 h-6" />
                            )}
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Menu Overlay */}
            {mobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={closeMobileMenu}
                />
            )}

            {/* Mobile Menu Slide-out */}
            <div className={`fixed top-16 right-0 h-[calc(100vh-4rem)] w-72 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out md:hidden ${mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
                }`}>
                <div className="flex flex-col h-full">
                    {/* Mobile Nav Items */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = pathname === item.href ||
                                (item.href !== '/' && pathname.startsWith(item.href));

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={closeMobileMenu}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                        ? 'bg-primary/10 text-primary font-medium'
                                        : 'text-gray-600 hover:bg-gray-100'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="text-base">{item.label}</span>
                                </Link>
                            );
                        })}

                        <Link
                            href="/reports"
                            onClick={closeMobileMenu}
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${pathname === '/reports'
                                ? 'bg-primary/10 text-primary font-medium'
                                : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            <FileText className="w-5 h-5" />
                            <span className="text-base">Reports</span>
                        </Link>
                    </div>

                    {/* Mobile User Section */}
                    <div className="border-t border-gray-100 p-4">
                        {user ? (
                            <div className="space-y-3">
                                <div className="flex items-center gap-2 text-sm text-gray-600 px-2">
                                    <User className="w-4 h-4" />
                                    <span className="truncate">{user.email}</span>
                                </div>
                                <button
                                    onClick={() => {
                                        closeMobileMenu();
                                        handleLogout();
                                    }}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-3 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                                >
                                    <LogOut className="w-5 h-5" />
                                    <span className="text-base font-medium">Logout</span>
                                </button>
                            </div>
                        ) : (
                            <Link
                                href="/login"
                                onClick={closeMobileMenu}
                                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                            >
                                <Play className="w-5 h-5" />
                                <span className="text-base font-medium">Get Started</span>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
