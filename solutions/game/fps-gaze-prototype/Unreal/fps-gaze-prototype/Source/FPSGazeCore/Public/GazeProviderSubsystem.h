#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GazeSignalTypes.h"
#include "GazeProviderSubsystem.generated.h"

class UGazeProviderSettings;
class UObject;

UCLASS()
class FPSGAZECORE_API UGazeProviderSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    bool IsEnabled() const;

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    void SetEnabled(bool bInEnabled);

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    bool ToggleEnabled();

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    FString GetSelectedProvider() const;

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    bool SetProvider(const FString& InProvider);

    UFUNCTION(BlueprintCallable, Category = "Gaze")
    FGazeSampleNormalized GetGatedSample() const;

    bool WriteStage1Artifacts() const;

private:
    UObject* BuildProvider(const FString& ProviderName) const;
    FGazeSampleNormalized ApplyConfidenceGate(const FGazeSampleNormalized& RawSample) const;
    double GetMonotonicNow() const;

private:
    UPROPERTY()
    TObjectPtr<UObject> ActiveProvider;

    UPROPERTY()
    bool bEnabled = true;

    UPROPERTY()
    FString ProviderName = TEXT("Null");

    UPROPERTY()
    float ConfidenceThreshold = 0.60f;
};
