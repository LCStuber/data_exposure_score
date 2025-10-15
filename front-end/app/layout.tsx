import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'
import './colors.css'
import ThemeToggle from './components/theme-toggle'


export const metadata: Metadata = {
  title: "Data Exposure Score",
  description: "Ferramenta para análise de exposição de dados em bancos de dados públicos.",
  icons: {
    icon: '/desicon.svg',
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        {/* Favicon (use absolute path and query param to bust cache) */}
        <link rel="icon" href="/desicon.svg?v=1" />
        <script
          dangerouslySetInnerHTML={{
            __html: `(()=>{try{if(localStorage.getItem('theme')==='dark'){document.documentElement.classList.add('dark');}}catch(_){}})();`,
          }}
        />
      </head>
      <body className={`${GeistSans.variable} ${GeistMono.variable} min-h-screen bg-[var(--color-bg)] text-[var(--color-foreground)] transition-colors duration-1000`}>        
        {children}
        {/* <ThemeToggle /> */}
      </body>
    </html>
  )
}