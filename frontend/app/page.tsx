import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-6">
            <Link href="/tenants" className="text-ink-muted hover:text-ink transition-colors flex items-center gap-1">
              <span>🔍</span> 浏览家族
            </Link>
            <Link href="/login" className="text-ink-muted hover:text-ink transition-colors">登录</Link>
            <Link href="/register" className="bg-vermillion text-white px-4 py-2 rounded-lg hover:bg-vermillion-dark transition-colors flex items-center gap-1">
              <span>✨</span> 创建族谱
            </Link>
          </div>
          
          <Link href="/register" className="md:hidden bg-vermillion text-white px-4 py-2 rounded-lg text-sm">
            开始
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          {/* Seal */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-vermillion/10 text-vermillion text-3xl font-serif font-bold mb-8 border-2 border-vermillion/20">
            谱
          </div>
          
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-ink mb-6">
            传承家族记忆
            <span className="block text-vermillion mt-2">让血脉有迹可循 🌳</span>
          </h1>
          
          <p className="text-lg text-ink-muted max-w-2xl mx-auto mb-10">
            现代化的多家族族谱管理平台。支持族谱树可视化、成员协作、历史记录，
            为每个家族打造专属的数字传承空间。
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/register" className="bg-vermillion text-white px-8 py-4 rounded-lg hover:bg-vermillion-dark transition-colors font-medium flex items-center justify-center gap-2">
              🚀 免费创建族谱
            </Link>
            <Link href="/tenants" className="bg-white text-ink border border-ink/10 px-8 py-4 rounded-lg hover:bg-paper-warm transition-colors font-medium flex items-center justify-center gap-2">
              👀 浏览公开家族
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 mt-16 pt-16 border-t border-ink/10">
            <div className="text-center">
              <div className="text-3xl font-serif font-semibold text-ink">100+</div>
              <div className="text-sm text-ink-muted mt-1">👨‍👩‍👧‍👦 家族入驻</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-serif font-semibold text-vermillion">10万+</div>
              <div className="text-sm text-ink-muted mt-1">👤 人物记录</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-serif font-semibold text-ink">500+</div>
              <div className="text-sm text-ink-muted mt-1">📜 世代传承</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-paper-warm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-serif font-semibold mb-4">✨ 核心功能</h2>
            <p className="text-ink-muted text-lg">专为家族传承设计</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard 
              icon="🌳" 
              title="族谱树可视化" 
              description="直观的家族树展示，支持缩放、拖拽、搜索，清晰呈现世代脉络" 
            />
            <FeatureCard 
              icon="✍️" 
              title="多人协作编辑" 
              description="邀请家族成员共同维护，角色权限管理，数据变更可追溯" 
            />
            <FeatureCard 
              icon="📸" 
              title="多媒体档案" 
              description="上传照片、视频、文档，记录家族珍贵记忆" 
            />
            <FeatureCard 
              icon="🔍" 
              title="智能检索" 
              description="快速定位家族成员，支持姓名、辈份、年代等多维度筛选" 
            />
            <FeatureCard 
              icon="📱" 
              title="多端适配" 
              description="PC端大屏展示，移动端便捷查看，随时随地查阅族谱" 
            />
            <FeatureCard 
              icon="🔒" 
              title="隐私保护" 
              description="多级隐私设置，敏感信息可控，保护家族数据安全" 
            />
          </div>
        </div>
      </section>

      {/* Steps Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-serif font-semibold mb-4">🎯 三步创建您的族谱</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-12">
            <StepCard number="1️⃣" title="注册账号" description="免费注册，创建您的家族空间" />
            <StepCard number="2️⃣" title="录入成员" description="添加家族成员，建立人物关系" />
            <StepCard number="3️⃣" title="邀请协作" description="分享给家族成员，共同完善族谱" />
          </div>
          
          <div className="text-center mt-16">
            <Link href="/register" className="bg-vermillion text-white px-10 py-4 rounded-lg hover:bg-vermillion-dark transition-colors font-medium text-lg inline-flex items-center gap-2">
              🎉 立即开始
            </Link>
          </div>
        </div>
      </section>

      {/* Quote Section */}
      <section className="py-20 bg-ink text-white">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <div className="text-4xl mb-6">📖</div>
          <blockquote className="text-2xl md:text-3xl font-serif leading-relaxed mb-8">
            参天之木，必有其根；<br/>
            怀山之水，必有其源。
          </blockquote>
          <cite className="text-white/60 text-lg">— 欧阳修《泷冈阡表》</cite>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <div className="text-5xl mb-6">🏡</div>
          <h2 className="text-3xl font-serif font-semibold mb-4">开启您的家族传承之旅</h2>
          <p className="text-ink-muted text-lg mb-8">免费创建，永久保存，让家族记忆代代相传</p>
          <Link href="/register" className="bg-vermillion text-white px-8 py-4 rounded-lg hover:bg-vermillion-dark transition-colors font-medium text-lg inline-flex items-center gap-2">
            🌟 免费创建族谱
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-ink/10">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-ink-muted">
          <p>📜 © 2026 族谱云 · 传承家族记忆</p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group">
      <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-ink-muted text-sm">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center group">
      <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">{number}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-ink-muted text-sm">{description}</p>
    </div>
  );
}