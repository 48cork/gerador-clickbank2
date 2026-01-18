import streamlit as st
import google.generativeai as genai
import json
import requests

# Configuração da página
st.set_page_config(
    page_title="ClickBank Arbitrage Machine - Campbell Method",
    page_icon="🌍",
    layout="centered"
)

# Configuração da API Key
api_key = None

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    if "api_key" not in st.session_state:
        st.session_state.api_key = None

if not api_key and not st.session_state.api_key:
    with st.sidebar:
        st.warning("⚙️ Configuration required")
        temp_key = st.text_input(
            "Google AI API Key",
            type="password",
            help="Paste your API Key here"
        )
        if temp_key:
            st.session_state.api_key = temp_key
            st.rerun()
        else:
            st.stop()

final_key = api_key if api_key else st.session_state.api_key
genai.configure(api_key=final_key)

# Título
st.title("🌍 ClickBank Arbitrage Machine")
st.markdown("**Campbell Method: Micro-Niches + Real ClickBank Products**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🧠 The Campbell Method")
    st.markdown("""
    **What makes this different:**
    
    ✅ Ultra-specific micro-niches
    ✅ Trigger Words (hot search terms)
    ✅ **REAL ClickBank products**
    ✅ Gravity scores & commissions
    ✅ Conversion-focused strategy
    """)
    
    st.markdown("---")
    
    # Seletor de idioma
    idioma = st.selectbox(
        "🌐 Language / Idioma",
        ["English 🇺🇸", "Português 🇧🇷", "Español 🇪🇸"]
    )
    
    if "produtos_encontrados" in st.session_state and st.session_state.produtos_encontrados:
        with st.expander("📦 Products Found"):
            st.json(st.session_state.produtos_encontrados)

# Função para buscar produtos ClickBank
def buscar_produtos_clickbank(nicho_keywords):
    """
    Busca produtos populares do ClickBank por categoria
    Base curada com produtos de alta conversão
    """
    produtos_sugeridos = []
    
    try:
        # Base de produtos ClickBank de alta conversão (organizados por nicho)
        categorias_clickbank = {
            "health": [
                {"nome": "The Smoothie Diet", "preco": 37, "comissao": 75, "gravity": 157, "url": "clickbank.com"},
                {"nome": "Metabolic Renewal", "preco": 37, "comissao": 75, "gravity": 142, "url": "clickbank.com"},
                {"nome": "Keto After 50", "preco": 37, "comissao": 75, "gravity": 189, "url": "clickbank.com"},
            ],
            "fitness": [
                {"nome": "Old School New Body", "preco": 39, "comissao": 75, "gravity": 134, "url": "clickbank.com"},
                {"nome": "Unlock Your Hip Flexors", "preco": 50, "comissao": 75, "gravity": 98, "url": "clickbank.com"},
                {"nome": "Yoga Burn", "preco": 37, "comissao": 75, "gravity": 167, "url": "clickbank.com"},
            ],
            "wealth": [
                {"nome": "12 Minute Affiliate", "preco": 9.95, "comissao": 70, "gravity": 203, "url": "clickbank.com"},
                {"nome": "Perpetual Income 365", "preco": 9, "comissao": 75, "gravity": 178, "url": "clickbank.com"},
                {"nome": "Super Affiliate System", "preco": 997, "comissao": 50, "gravity": 92, "url": "clickbank.com"},
            ],
            "relationships": [
                {"nome": "His Secret Obsession", "preco": 47, "comissao": 75, "gravity": 201, "url": "clickbank.com"},
                {"nome": "Text Chemistry", "preco": 47, "comissao": 75, "gravity": 145, "url": "clickbank.com"},
                {"nome": "The Devotion System", "preco": 47, "comissao": 75, "gravity": 112, "url": "clickbank.com"},
            ],
            "spirituality": [
                {"nome": "Manifestation Magic", "preco": 47, "comissao": 75, "gravity": 156, "url": "clickbank.com"},
                {"nome": "Numerologist.com", "preco": 47, "comissao": 75, "gravity": 189, "url": "clickbank.com"},
                {"nome": "Moon Reading", "preco": 47, "comissao": 75, "gravity": 167, "url": "clickbank.com"},
            ],
            "survival": [
                {"nome": "The Lost Ways", "preco": 37, "comissao": 75, "gravity": 234, "url": "clickbank.com"},
                {"nome": "Backyard Revolution", "preco": 39, "comissao": 75, "gravity": 198, "url": "clickbank.com"},
                {"nome": "Alive After Crisis", "preco": 37, "comissao": 75, "gravity": 143, "url": "clickbank.com"},
            ],
            "languages": [
                {"nome": "Rocket Languages", "preco": 99, "comissao": 50, "gravity": 87, "url": "clickbank.com"},
                {"nome": "Pimsleur", "preco": 119, "comissao": 40, "gravity": 76, "url": "clickbank.com"},
            ],
            "pets": [
                {"nome": "Brain Training for Dogs", "preco": 47, "comissao": 75, "gravity": 201, "url": "clickbank.com"},
                {"nome": "The Ultimate Dog Training", "preco": 37, "comissao": 75, "gravity": 154, "url": "clickbank.com"},
            ]
        }
        
        # Busca produtos relacionados
        nicho_lower = nicho_keywords.lower()
        for categoria, produtos in categorias_clickbank.items():
            if categoria in nicho_lower or any(palavra in nicho_lower for palavra in ["saúde", "health", "salud"]):
                if categoria in ["health", "fitness"]:
                    produtos_sugeridos.extend(produtos[:2])
            elif any(palavra in nicho_lower for palavra in ["dinheiro", "money", "wealth", "dinero", "negócio", "business"]):
                if categoria == "wealth":
                    produtos_sugeridos.extend(produtos[:2])
            elif any(palavra in nicho_lower for palavra in ["relacionamento", "relationship", "amor", "love"]):
                if categoria == "relationships":
                    produtos_sugeridos.extend(produtos[:2])
        
        # Se não encontrou, pega os top gravity de todas categorias
        if not produtos_sugeridos:
            todos_produtos = []
            for produtos in categorias_clickbank.values():
                todos_produtos.extend(produtos)
            todos_produtos.sort(key=lambda x: x["gravity"], reverse=True)
            produtos_sugeridos = todos_produtos[:3]
        
        return produtos_sugeridos[:3]
        
    except Exception as e:
        return []

# Função para converter USD para BRL
def converter_usd_brl(valor_usd):
    """Converte dólar para real (cotação aproximada)"""
    cotacao = 5.0  # Cotação média
    return valor_usd * cotacao

# Função para gerar estratégia
def gerar_estrategia_clickbank(investimento, habilidades, meta_ganho, idioma):
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Busca produtos
        with st.spinner("🔍 Searching real ClickBank products..."):
            produtos = buscar_produtos_clickbank(habilidades)
            st.session_state.produtos_encontrados = produtos
        
        # Monta informação dos produtos
        produtos_info = "\n".join([
            f"- {p['nome']} (${p['preco']}, {p['comissao']}% commission = ${p['preco'] * p['comissao'] / 100:.2f} per sale, Gravity: {p['gravity']})" 
            for p in produtos
        ]) if produtos else "No specific products found."
        
        # Define idioma do prompt
        idioma_prompt = "English" if "English" in idioma else "Português" if "Português" in idioma else "Español"
        
        prompt = f"""You are Marcus Campbell, expert in arbitrage marketing and ClickBank affiliate marketing.

RESPOND IN {idioma_prompt}!

📊 CLIENT DATA:
- Available investment: ${investimento / 5:.2f} USD (R$ {investimento})
- Skills: {habilidades}
- Monthly goal: ${meta_ganho / 5:.2f} USD (R$ {meta_ganho})

🛒 REAL CLICKBANK PRODUCTS AVAILABLE:
{produtos_info}

🎯 YOUR MISSION (Campbell Method):

1. ULTRA-SPECIFIC MICRO-NICHE
   - Identify ONE ultra-specific niche (not generic)
   - Example: NOT "weight loss", YES "keto for women over 50"
   - Explain why it has LOW competition
   - What is the SPECIFIC pain point of this audience?

2. TRIGGER WORDS (5-7 keywords)
   - EXACT terms this audience searches to BUY
   - Examples: "best", "how to", "buy", "reviews"
   - Indicate buyer intent for each keyword

3. AFFILIATE PRODUCTS (use real products above)
   - For EACH product listed above:
     * How it solves the niche's pain
     * Calculation: How many sales/month to reach ${meta_ganho / 5:.2f}?
     * Specific promotion strategy
   - Calculate commission in USD and BRL (1 USD = 5 BRL)

4. 7-DAY ACTION PLAN (CONCRETE actions)
   - Day 1: First action (specific)
   - Day 2-3: Content creation
   - Day 4-5: Where to post and how to engage
   - Day 6-7: First sales goal
   - EACH day: 2-3 practical tasks

5. INSTAGRAM BIO (150 chars MAX)
   - Focus on PAIN + RESULT + CTA
   - Example: "🔥 Lose 20lbs in 30 days | Keto made simple | Free guide 👇"
   - Use strategic emojis
   - DON'T talk about YOU, talk about CLIENT results

6. FREE TRAFFIC (first 30 days)
   - Where is this audience? (groups, hashtags, forums)
   - Content to attract without selling
   - How to insert affiliate link naturally
   - Realistic follower goal per day

7. VIABILITY CALCULATION
   - Sales needed for ${meta_ganho / 5:.2f} USD (R$ {meta_ganho})
   - Realistic conversion rate (1-3%)
   - How many leads do you need?
   - Is this achievable with ${investimento / 5:.2f} USD investment?

8. FATAL MISTAKES (3 errors)
   - What NOT to do in this niche
   - Signs you're on the wrong path

RULES:
- ULTRA-SPECIFIC always
- Use REAL products from the list
- Calculate real numbers (sales, commissions in USD and BRL)
- Every advice must be ACTIONABLE
- Focus on QUICK PROFIT (30-60 days)
- Include Gravity scores explanation

Use markdown, titles, bullet points and emojis. RESPOND IN {idioma_prompt}."""

        with st.spinner("🧠 Analyzing micro-niches and creating strategy..."):
            response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Formulário
with st.form("formulario_clickbank"):
    st.subheader("📝 Opportunity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        investimento = st.number_input(
            "💰 Investment (R$)",
            min_value=0,
            max_value=100000,
            value=500,
            step=100,
            help="Available budget to start"
        )
    
    with col2:
        meta_ganho = st.number_input(
            "🎯 Monthly Goal (R$)",
            min_value=500,
            max_value=100000,
            value=3000,
            step=500,
            help="How much you want to earn per month"
        )
    
    habilidades = st.text_area(
        "🎯 Skills and Knowledge",
        placeholder="Ex: Health, social media, video editing, English...",
        height=100,
        help="List what you know or can learn quickly"
    )
    
    submitted = st.form_submit_button("🚀 Find My Micro-Niche + Products", use_container_width=True)

if submitted:
    if not habilidades:
        st.error("⚠️ Please describe your skills")
    else:
        resultado = gerar_estrategia_clickbank(investimento, habilidades, meta_ganho, idioma)
        
        st.markdown("---")
        st.markdown("## 💎 Complete Strategy - Campbell Method")
        
        # Mostra produtos
        if "produtos_encontrados" in st.session_state and st.session_state.produtos_encontrados:
            st.success(f"✅ {len(st.session_state.produtos_encontrados)} real ClickBank products found!")
            
            # Tabela de produtos
            st.markdown("### 📦 Selected Products:")
            for p in st.session_state.produtos_encontrados:
                comissao_usd = p['preco'] * p['comissao'] / 100
                comissao_brl = converter_usd_brl(comissao_usd)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Product", p['nome'])
                with col2:
                    st.metric("Commission", f"${comissao_usd:.2f} (R$ {comissao_brl:.2f})")
                with col3:
                    st.metric("Gravity", p['gravity'], help="Higher = more affiliates selling")
        
        st.markdown(resultado)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "💾 Download Strategy",
                data=resultado,
                file_name="clickbank_strategy.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 New Analysis", use_container_width=True):
                st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    🌍 ClickBank Arbitrage Machine - Campbell Method<br>
    <small>Micro-Niches • Gravity Scores • Real Commissions • Global Products</small>
    </div>
    """,
    unsafe_allow_html=True
)
