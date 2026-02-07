#pragma once

#include "CoreMinimal.h"
#include "GazeSignalTypes.h"
#include "GazeIntentTypes.generated.h"

USTRUCT(BlueprintType)
struct FGazeScreenRect
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    float MinX = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    float MinY = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    float MaxX = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    float MaxY = 1.0f;

    bool Contains(const FVector2D& Point) const
    {
        return Point.X >= MinX && Point.X <= MaxX && Point.Y >= MinY && Point.Y <= MaxY;
    }
};

USTRUCT(BlueprintType)
struct FGazeIntentSceneTarget
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FString Id;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    bool bAimable = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    bool bInteractable = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    bool bUiElement = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FGazeScreenRect ScreenRegion;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    int32 Priority = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    TArray<FString> Tags;
};

USTRUCT(BlueprintType)
struct FGazeUiFocusZone
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FString Name;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FGazeScreenRect ScreenRegion;
};

USTRUCT(BlueprintType)
struct FGazeIntentSceneModel
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    TArray<FGazeIntentSceneTarget> Targets;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    TArray<FGazeUiFocusZone> UiZones;
};

USTRUCT(BlueprintType)
struct FGazeIntentResolverSettings
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    bool bEnabled = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    EGazeProviderSource Provider = EGazeProviderSource::Null;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    float ConfidenceThreshold = 0.60f;
};

UENUM(BlueprintType)
enum class EAimIntentTargetKind : uint8
{
    None = 0,
    ActorId = 1,
    Location = 2,
};

USTRUCT(BlueprintType)
struct FAimIntentTarget
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    EAimIntentTargetKind Kind = EAimIntentTargetKind::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FString ActorId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FVector Location = FVector::ZeroVector;

    static FAimIntentTarget MakeActor(const FString& InActorId)
    {
        FAimIntentTarget Target;
        Target.Kind = EAimIntentTargetKind::ActorId;
        Target.ActorId = InActorId;
        return Target;
    }

    static FAimIntentTarget MakeLocation(const FVector& InLocation)
    {
        FAimIntentTarget Target;
        Target.Kind = EAimIntentTargetKind::Location;
        Target.Location = InLocation;
        return Target;
    }
};

UENUM(BlueprintType)
enum class EInteractIntentTargetKind : uint8
{
    None = 0,
    ActorId = 1,
    UiElement = 2,
};

USTRUCT(BlueprintType)
struct FInteractIntentTarget
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    EInteractIntentTargetKind Kind = EInteractIntentTargetKind::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FString ReferenceId;

    static FInteractIntentTarget MakeActor(const FString& InActorId)
    {
        FInteractIntentTarget Target;
        Target.Kind = EInteractIntentTargetKind::ActorId;
        Target.ReferenceId = InActorId;
        return Target;
    }

    static FInteractIntentTarget MakeUiElement(const FString& InUiId)
    {
        FInteractIntentTarget Target;
        Target.Kind = EInteractIntentTargetKind::UiElement;
        Target.ReferenceId = InUiId;
        return Target;
    }
};

USTRUCT(BlueprintType)
struct FGazeIntentOutput
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FAimIntentTarget AimIntentTarget;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FInteractIntentTarget InteractIntentTarget;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze|Intent")
    FString UIFocusZone;

    static FGazeIntentOutput MakeNullIntent()
    {
        FGazeIntentOutput Output;
        Output.AimIntentTarget = FAimIntentTarget();
        Output.InteractIntentTarget = FInteractIntentTarget();
        Output.UIFocusZone.Empty();
        return Output;
    }
};
