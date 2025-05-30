from kivy.utils import platform
from kivy.app import App
from kivy.logger import Logger

if (platform == 'android'):
    from jnius import autoclass, cast
    # 导入Android Java类
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    String = autoclass('java.lang.String')
    Context = autoclass('android.content.Context')
    class ShareManager:
        def __init__(self):
            self.download_link = "https://play.google.com/store/apps/details?id=org.ayde.jumpgame"

        def start_share(self):
            self.player_info=App.get_running_app().data
            share_text = (
                "Use your face to beat monsters "
                "World's first facial motion-controlled mobile game. "
                f"I have shaken my face reached the {self.player_info.get('current_level')} level. "
                f"Come on with me quickly: {self.download_link} "  # 注意这里保持f前缀
            )
            # 创建Intent对象
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType("text/plain")
            intent.putExtra(Intent.EXTRA_TEXT, String(share_text))

            # 获取当前Activity
            current_activity = cast('android.app.Activity', PythonActivity.mActivity)

            # 启动分享对话框
            chooser = Intent.createChooser(intent, cast('java.lang.CharSequence', String("Share to")))
            current_activity.startActivity(chooser)
