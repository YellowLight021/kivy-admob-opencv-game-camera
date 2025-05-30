package org.test.google_update;

import android.app.Activity;
import android.util.Log;

import com.google.android.play.core.appupdate.AppUpdateInfo;
import com.google.android.play.core.appupdate.AppUpdateManager;
import com.google.android.play.core.appupdate.AppUpdateManagerFactory;
import com.google.android.play.core.install.model.AppUpdateType;
import com.google.android.play.core.install.model.UpdateAvailability;
import com.google.android.play.core.install.model.InstallStatus;
import com.google.android.gms.tasks.OnSuccessListener;

public class UpdateHelper {

    private static final int REQUEST_CODE = 201926;

    public static void checkForUpdate(Activity activity) {
        AppUpdateManager appUpdateManager = AppUpdateManagerFactory.create(activity);

        appUpdateManager.getAppUpdateInfo().addOnSuccessListener(
            new OnSuccessListener<AppUpdateInfo>() {
                @Override
                public void onSuccess(AppUpdateInfo appUpdateInfo) {
                    Log.d("UpdateHelper", "Update check: success");

                    int updateAvailability = appUpdateInfo.updateAvailability();
                    int installStatus = appUpdateInfo.installStatus();

                    Log.d("UpdateHelper", "updateAvailability: " + updateAvailability);
                    Log.d("UpdateHelper", "installStatus: " + installStatus);

                   
                    if (installStatus == InstallStatus.DOWNLOADED) {
                        Log.d("UpdateHelper", "Update already downloaded, completing update...");
                        appUpdateManager.completeUpdate();
                        return;
                    }

                   
                    if (updateAvailability == UpdateAvailability.UPDATE_AVAILABLE &&
                        appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)) {

                        Log.d("UpdateHelper", "Starting update flow...");
                        try {
                            appUpdateManager.startUpdateFlowForResult(
                                appUpdateInfo,
                                AppUpdateType.IMMEDIATE,
                                activity,
                                REQUEST_CODE
                            );
                        } catch (Exception e) {
                            Log.e("UpdateHelper", "Update flow failed: " + e.getMessage());
                        }
                    } else {
                        Log.d("UpdateHelper", "No update needed or not allowed.");
                    }
                }
            }
        );
    }
}
