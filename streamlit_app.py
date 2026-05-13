import streamlit as st
import requests
from io import BytesIO
from datetime import datetime
import random

# 页面配置
st.set_page_config(
    page_title="Random Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .history-item {
        background: #f0f2f6;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'image_history' not in st.session_state:
    st.session_state.image_history = []
if 'current_image_url' not in st.session_state:
    st.session_state.current_image_url = None
if 'current_seed' not in st.session_state:
    st.session_state.current_seed = None

def get_random_image_url(category="any", width=800, height=600, seed=None):
    """
    获取随机图片URL
    使用 Lorem Picsum 作为免费图片源
    """
    # 如果提供了种子，使用固定种子生成
    if seed is None:
        seed = random.randint(1, 1000000)
    
    # 基础URL - Lorem Picsum 提供高质量随机图片
    base_url = "https://picsum.photos"
    
    # 根据类别选择关键词（Picsum支持通过seed实现不同图片）
    # 不同种子对应不同图片，类别通过种子范围模拟
    if category != "any":
        # 使用类别作为种子前缀，确保同类图片有一定相似性但不完全相同
        category_seed_map = {
            "nature": (1, 10000),
            "people": (10001, 20000),
            "technology": (20001, 30000),
            "animals": (30001, 40000),
            "architecture": (40001, 50000),
            "art": (50001, 60000)
        }
        if category in category_seed_map:
            min_seed, max_seed = category_seed_map[category]
            seed = min_seed + (seed % (max_seed - min_seed))
    
    # 构建URL
    image_url = f"{base_url}/{width}/{height}?seed={seed}"
    
    return image_url, seed

def get_random_unsplash_image(width=800, height=600, query=None):
    """
    使用Unsplash Source API获取随机图片
    备用方案，提供更丰富的图片内容
    """
    if query:
        url = f"https://source.unsplash.com/random/{width}x{height}/?{query}"
    else:
        url = f"https://source.unsplash.com/random/{width}x{height}"
    return url

def generate_image():
    """生成随机图片"""
    # 获取用户设置
    source = st.session_state.get("image_source", "picsum")
    category = st.session_state.get("category", "any")
    width = st.session_state.get("width", 800)
    height = st.session_state.get("height", 600)
    use_fixed_seed = st.session_state.get("use_fixed_seed", False)
    custom_seed = st.session_state.get("custom_seed", None)
    
    if source == "picsum":
        if use_fixed_seed and custom_seed:
            seed = custom_seed
        else:
            seed = None
        image_url, used_seed = get_random_image_url(category, width, height, seed)
    else:
        # Unsplash source
        image_url = get_random_unsplash_image(width, height, category if category != "any" else None)
        used_seed = None
    
    return image_url, used_seed

def add_to_history(image_url, category, width, height, seed, source):
    """添加到历史记录"""
    st.session_state.image_history.insert(0, {
        "url": image_url,
        "category": category,
        "width": width,
        "height": height,
        "seed": seed,
        "source": source,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # 保留最近20条记录
    if len(st.session_state.image_history) > 20:
        st.session_state.image_history = st.session_state.image_history[:20]

def main():
    # 标题
    st.markdown('<div class="main-header">🎨 Random Image Generator</div>', unsafe_allow_html=True)
    st.markdown("Generate random images with customizable categories and sizes")
    
    # 创建三列布局：控制面板、图片显示、历史记录
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    with col_left:
        st.markdown("### ⚙️ Settings")
        
        # 图片源选择
        image_source = st.selectbox(
            "Image Source",
            ["picsum", "unsplash"],
            help="Picsum: Simple random images | Unsplash: High-quality photos",
            key="image_source"
        )
        
        # 分类选择
        categories = ["any", "nature", "people", "technology", "animals", "architecture", "art"]
        category = st.selectbox("Category", categories, key="category")
        
        # 尺寸设置
        col_w, col_h = st.columns(2)
        with col_w:
            width = st.number_input("Width (px)", min_value=100, max_value=1920, value=800, step=50, key="width")
        with col_h:
            height = st.number_input("Height (px)", min_value=100, max_value=1920, value=600, step=50, key="height")
        
        # 种子设置（仅Picsum支持）
        if image_source == "picsum":
            use_fixed_seed = st.checkbox("Use fixed seed", key="use_fixed_seed")
            if use_fixed_seed:
                custom_seed = st.number_input("Seed value", min_value=1, max_value=999999, value=12345, key="custom_seed")
            else:
                st.session_state.custom_seed = None
        
        # 生成按钮
        generate_btn = st.button("🎲 Generate Random Image", type="primary", use_container_width=True)
        
        # 关于信息
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("Picsum: Random placeholder images")
        st.caption("Unsplash: High-quality photos from Unsplash")
    
    with col_mid:
        st.markdown("### 🖼️ Generated Image")
        
        # 处理生成请求
        if generate_btn or st.session_state.current_image_url is None:
            with st.spinner("Generating image..."):
                image_url, used_seed = generate_image()
                st.session_state.current_image_url = image_url
                st.session_state.current_seed = used_seed
                
                # 添加到历史
                add_to_history(
                    image_url, 
                    st.session_state.get("category", "any"),
                    st.session_state.get("width", 800),
                    st.session_state.get("height", 600),
                    used_seed,
                    st.session_state.get("image_source", "picsum")
                )
        
        # 显示当前图片
        if st.session_state.current_image_url:
            # 图片容器
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(st.session_state.current_image_url, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 图片信息
            st.markdown(f"**Seed:** {st.session_state.current_seed if st.session_state.current_seed else 'Random'}")
            st.markdown(f"**Source:** {st.session_state.get('image_source', 'picsum').title()}")
            
            # 操作按钮
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("📥 Download", use_container_width=True):
                    try:
                        response = requests.get(st.session_state.current_image_url)
                        if response.status_code == 200:
                            st.download_button(
                                label="Click to save",
                                data=response.content,
                                file_name=f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                                mime="image/jpeg",
                                use_container_width=True
                            )
                        else:
                            st.error("Download failed")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col_btn2:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.rerun()
            
            with col_btn3:
                if st.button("📋 Copy URL", use_container_width=True):
                    st.info("URL copied to clipboard (select manually)")
                    st.code(st.session_state.current_image_url)
    
    with col_right:
        st.markdown("### 📜 History")
        
        if not st.session_state.image_history:
            st.info("No history yet. Generate some images!")
        else:
            for idx, item in enumerate(st.session_state.image_history[:10]):
                with st.container():
                    st.markdown(f"""
                    <div class="history-item">
                        <strong>{item['category'].title()}</strong> | {item['width']}x{item['height']}<br>
                        <span style="font-size:0.75rem; color:#888;">{item['timestamp']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_h1, col_h2 = st.columns([1, 1])
                    with col_h1:
                        if st.button("🖼️ View", key=f"view_{idx}"):
                            st.session_state.current_image_url = item['url']
                            st.session_state.current_seed = item.get('seed')
                            st.rerun()
                    with col_h2:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.image_history.pop(idx)
                            st.rerun()
        
        # 清空历史按钮
        if st.session_state.image_history:
            if st.button("Clear All History", key="clear_history", use_container_width=True):
                st.session_state.image_history = []
                st.rerun()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "Powered by Lorem Picsum & Unsplash | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
