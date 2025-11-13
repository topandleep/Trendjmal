from flask import Flask, render_template, request, jsonify
from hybrid_bot_engine import AIONHybridBot
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
bot = AIONHybridBot()

@app.route('/')
def dashboard():
    stats = bot.get_performance_stats()
    trades = bot.get_recent_trades()
    progress = bot.get_progress_data()
    
    # التحقق من اتصال البوت
    connection_status = "✅ متصل" if bot.client else "❌ غير متصل"
    
    return render_template(
        "dashboard.html",
        stats=stats,
        trades=trades,
        progress=progress,
        balance=bot.balance,
        connection_status=connection_status,
        has_keys=bot.api_key is not None
    )

@app.route('/start', methods=['POST'])
def start_bot():
    data = request.json
    api_key = data.get('api_key', '').strip()
    api_secret = data.get('api_secret', '').strip()
    mode = data.get('mode', 'DEMO')
    
    if not api_key or not api_secret:
        return jsonify({"error": "❌ يرجى إدخال كلا المفتاحين"}), 400
    
    if bot.set_keys(api_key, api_secret, mode):
        result = bot.start_trading()
        return jsonify({
            "status": result,
            "mode": mode,
            "target": f"${bot.target_balance}",
            "timeline": f"{bot.days_remaining} يوم",
            "has_keys": True
        })
    else:
        return jsonify({"error": "❌ فشل في تعيين المفاتيح - تحقق من المفاتيح واتصالك بالإنترنت"}), 400

@app.route('/stop', methods=['POST'])
def stop_bot():
    result = bot.stop_trading()
    return jsonify({"status": result})

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    start_date = data.get('start_date', '2024-01-01')
    end_date = data.get('end_date', '2024-01-31')
    
    result = bot.run_advanced_simulation(start_date, end_date)
    return jsonify(result)

@app.route('/stats')
def get_stats():
    return jsonify(bot.get_performance_stats())

@app.route('/progress')
def get_progress():
    return jsonify(bot.get_progress_data())

@app.route('/trades')
def get_trades():
    return jsonify(bot.get_recent_trades())

@app.route('/live-trades')
def get_live_trades():
    return jsonify(bot.get_live_trades())

@app.route('/balance-history')
def get_balance_history():
    return jsonify(bot.get_balance_history())

@app.route('/intelligence')
def get_intelligence():
    stats = bot.get_performance_stats()
    return jsonify(stats['adaptive_intelligence'])

@app.route('/test-api-keys', methods=['POST'])
def test_api_keys():
    """اختبار مفصل للمفاتيح"""
    try:
        data = request.json
        api_key = data.get('api_key', '').strip()
        api_secret = data.get('api_secret', '').strip()
        mode = data.get('mode', 'DEMO')
        
        if not api_key or not api_secret:
            return jsonify({
                "success": False,
                "message": "❌ يرجى إدخال كلا المفتاحين",
                "details": "المفاتيح لا يمكن أن تكون فارغة"
            })
        
        # اختبار الاتصال الفعلي
        from binance.client import Client
        client = Client(api_key, api_secret, testnet=(mode=='DEMO'))
        
        # اختبار جلب سعر حقيقي
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        btc_price = float(ticker['price'])
        
        # اختبار الحساب
        account_info = client.get_account()
        
        return jsonify({
            "success": True,
            "message": f"✅ المفاتيح صحيحة - سعر BTC: ${btc_price:,.2f}",
            "details": {
                "can_trade": account_info.get('canTrade', False),
                "account_type": "Testnet" if mode == "DEMO" else "Real",
                "balances_count": len(account_info.get('balances', [])),
                "btc_price": btc_price,
                "server_time": client.get_server_time()['serverTime']
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        details = "خطأ غير معروف"
        
        if "Invalid API-key" in error_msg:
            details = "مفتاح API غير صحيح - تأكد من نسخه من testnet.binance.vision"
        elif "Signature" in error_msg:
            details = "مفتاح Secret غير صحيح - تأكد من نسخه بشكل كامل"
        elif "restrictions" in error_msg.lower():
            details = "قيود جغرافية - قد تحتاج VPN"
        elif "connection" in error_msg.lower():
            details = "مشكلة في الاتصال - تحقق من الإنترنت"
        
        return jsonify({
            "success": False,
            "message": "❌ فشل في الاتصال",
            "details": details,
            "error": error_msg
        })

@app.route('/clear-keys', methods=['POST'])
def clear_keys():
    """مسح المفاتيح المحفوظة"""
    try:
        if os.path.exists(bot.keys_file):
            os.remove(bot.keys_file)
        bot.api_key = None
        bot.api_secret = None
        bot.client = None
        return jsonify({"status": "✅ تم مسح المفاتيح"})
    except Exception as e:
        return jsonify({"error": f"❌ خطأ في مسح المفاتيح: {e}"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
