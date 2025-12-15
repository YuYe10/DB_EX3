import logging
from app import app, Config
from logger_config import Colors

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # 显示启动信息
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_GREEN}")
    print("=" * 60)
    print("🚀 学生选课与成绩管理系统后端 - 启动中...")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    logger.info(f"ℹ️ Server Configuration:")
    logger.info(f"   Host: {Config.HOST}")
    logger.info(f"   Port: {Config.PORT}")
    logger.info(f"   Debug: {Config.DEBUG}")
    logger.info(f"   Database: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    
    print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}\n")
    
    try:
        logger.info("✅ Starting Flask application server...")
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
    except KeyboardInterrupt:
        logger.info("⚠️  Server interrupted by user")
        print(f"\n{Colors.BRIGHT_YELLOW}{'─' * 60}")
        print("🛑 服务器已停止")
        print(f"{'─' * 60}{Colors.RESET}\n")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        raise
