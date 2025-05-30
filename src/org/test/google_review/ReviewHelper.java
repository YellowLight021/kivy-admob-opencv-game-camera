package org.test.google_review;

import android.app.Activity;
import android.util.Log;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;

import androidx.annotation.NonNull;

public class ReviewHelper {
    private static final String TAG = "ReviewHelper";
    private final Activity activity;
    private final ReviewManager reviewManager;

    public ReviewHelper(Activity activity) {
        this.activity = activity;
        this.reviewManager = ReviewManagerFactory.create(activity);
    }

    public void requestReview() {
        Log.d(TAG, "Starting requestReviewFlow");
        Task<ReviewInfo> request = reviewManager.requestReviewFlow();
        request.addOnSuccessListener(new OnSuccessListener<ReviewInfo>() {
            @Override
            public void onSuccess(ReviewInfo reviewInfo) {
                Log.d(TAG, "Successfully retrieved ReviewInfo");
                launchReviewFlow(reviewInfo);
            }
        });
        request.addOnFailureListener(new OnFailureListener() {
            @Override
            public void onFailure(@NonNull Exception e) {
                Log.e(TAG, "Failed to retrieve ReviewInfo: " + e.getMessage());
               // Toast.makeText(activity, "Review unavailable", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void launchReviewFlow(ReviewInfo reviewInfo) {
        Task<Void> flow = reviewManager.launchReviewFlow(activity, reviewInfo);
        flow.addOnCompleteListener(new OnCompleteListener<Void>() {
            @Override
            public void onComplete(@NonNull Task<Void> task) {
                Log.d(TAG, "Review flow finished");
                //Toast.makeText(activity, "Review flow completed", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
