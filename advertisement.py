from kivy.utils import platform
from kivy.app import App
from kivy.logger import Logger
if (platform == 'android'):
    # Get path to internal Android Storage
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    from kivmob_mod import KivMob, TestIds, RewardedListenerInterface


    class RewardsHandler(RewardedListenerInterface):
        def on_rewarded(self, reward_type, reward_amount):
            print("******************")
            # load rewarded_ads
            reward_context=App.get_running_app().adMob.reward_context
            print(reward_context)
            rewardType,rewardNum=reward_context.split(":")
            print("rewardType,rewardNum:{},{}".format(rewardType,rewardNum))
            if rewardType=="revive":
                App.get_running_app().sm.get_screen("game").level_instance.revive_charater()
                App.get_running_app().sm.get_screen("game").level_instance.start_process()
            elif rewardType=="coin":
                print("reward coin:{}".format(App.get_running_app().sm.get_screen("menu").player_info['money']))
                App.get_running_app().sm.get_screen("menu").player_info['money']+=int(rewardNum)
                print("reward coin:{}".format(App.get_running_app().sm.get_screen("menu").player_info['money']))
                App.get_running_app().sm.get_screen("game").level_instance.set_task_complete()
            App.get_running_app().adMob.load_ads()  # テスト用
            print("******************")

    class AdMobManager:
        def __init__(self):
            self.ads = KivMob(TestIds.APP)  # テスト用
            # banner
            self.ads.new_banner(TestIds.BANNER, top_pos=False)  # テスト用
            self.ads.request_banner()
            self.banner_is_working=False
            self.banner_visible = False  # 追踪广告是否显示
            self.reward_context = None  # 当前的奖励上下文,用于激励视频奖励
            # self.ads.show_banner()
            # interstitial
            # self.ads.load_interstitial(TestIds.INTERSTITIAL)  # テスト用
            # rewarded_ad
            self.load_ads()
            # self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)  # テスト用
            # RewardedAdLoadCallback4kivyを継承したRewardsHandlerのインスタンスをset_rewarded_ad_listenerに渡す
            self.ads.set_rewarded_ad_listener(RewardsHandler())

        def load_ads(self):
            if platform == 'android':
                Logger.info("kivmob_test: load_ads() fired")
                # banner
                self.ads.request_banner()
                # interstitial
                # self.ads.load_interstitial(TestIds.INTERSTITIAL)  # テスト用
                # rewarded_ad
                self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)  # テスト用

        def show_banner(self):
            if platform == 'android':
                Logger.info("kivmob_test: show_banner() fired")
                self.ads.show_banner()
                self.banner_visible=True

        def hide_banner(self):
            if platform == 'android':
                if self.banner_visible:
                    Logger.info("kivmob_test: hide_banner() fired")
                    self.ads.hide_banner()
                    self.banner_visible = False

        def refresh_banner(self, dt=None):
            self.hide_banner()
            self.ads.request_banner()
            self.show_banner()
        def load_rewarded_ad(self):
            if platform == 'android':
                Logger.info("kivmob_test: load_rewarded_ad() fired")
                self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)  # テスト用

        def if_load_rewarded_ad(self):
            if platform == 'android':
                return self.ads.load_rewarded_is_success()
            return False
        def show_rewarded_ad(self):
            if platform == 'android':
                Logger.info("kivmob_test: show_rewarded_ad() fired")
                self.ads.show_rewarded_ad()