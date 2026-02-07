#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "GazeProviderSettings.generated.h"

UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Gaze Provider Settings"))
class FPSGAZECORE_API UGazeProviderSettings : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    UGazeProviderSettings();

    UPROPERTY(EditAnywhere, Config, BlueprintReadOnly, Category = "Gaze", meta = (DisplayName = "Gaze.Enabled"))
    bool bGazeEnabled;

    UPROPERTY(EditAnywhere, Config, BlueprintReadOnly, Category = "Gaze", meta = (DisplayName = "Gaze.Provider"))
    FString GazeProvider;

    UPROPERTY(EditAnywhere, Config, BlueprintReadOnly, Category = "Gaze", meta = (DisplayName = "Gaze.ConfidenceThreshold", ClampMin = "0.0", ClampMax = "1.0"))
    float ConfidenceThreshold;
};
