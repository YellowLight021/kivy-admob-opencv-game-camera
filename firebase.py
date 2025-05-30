from kivy.utils import platform
from kivy.app import App
from kivy.logger import Logger

if platform == 'android':
    from jnius import autoclass



    class AppLogEventManager:
        def __init__(self):
            FirebaseAnalytics = autoclass('com.google.firebase.analytics.FirebaseAnalytics')
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            self.firebase_analytics = FirebaseAnalytics.getInstance(context)

        def log_event(self, event_name, params):
            # 创建一个 Bundle 对象
            bundle = autoclass('android.os.Bundle')()

            # 遍历 params 字典，处理传入的参数
            for key, value in params.items():
                # 确保 value 转换为字符串
                if isinstance(value, str):
                    bundle.putString(key, value)
                elif isinstance(value, int):
                    bundle.putInt(key, value)
                elif isinstance(value, float):
                    bundle.putDouble(key, value)
                else:
                    Logger.warning(f"Unsupported value type for key {key}: {type(value)}")

            # 记录 Firebase 事件
            try:
                self.firebase_analytics.logEvent(event_name, bundle)
                Logger.info(f"Logged event: {event_name} with params: {params}")
            except Exception as e:
                Logger.error(f"Error logging event {event_name}: {str(e)}")
