#include "GazeProviderSubsystem.h"

#include "GazeProviderInterface.h"
#include "GazeProviderSettings.h"
#include "Providers/NullGazeProvider.h"
#include "Providers/TobiiGazeProvider.h"

#include "HAL/IConsoleManager.h"
#include "HAL/PlatformFilemanager.h"
#include "HAL/PlatformTime.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
UGazeProviderSubsystem* ResolveSubsystemFromWorld(const TArray<FString>& Args)
{
    UWorld* World = nullptr;
    if (GEngine != nullptr)
    {
        for (const FWorldContext& Context : GEngine->GetWorldContexts())
        {
            if (Context.WorldType == EWorldType::Game || Context.WorldType == EWorldType::PIE)
            {
                World = Context.World();
                break;
            }
        }
    }

    if (World == nullptr || World->GetGameInstance() == nullptr)
    {
        UE_LOG(LogTemp, Warning, TEXT("Gaze console command requires an active game world"));
        return nullptr;
    }

    return World->GetGameInstance()->GetSubsystem<UGazeProviderSubsystem>();
}

static FAutoConsoleCommand GazeToggleCommand(
    TEXT("Gaze.Toggle"),
    TEXT("Toggle Gaze.Enabled at runtime"),
    FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
    {
        if (UGazeProviderSubsystem* Subsystem = ResolveSubsystemFromWorld(Args))
        {
            const bool bNowEnabled = Subsystem->ToggleEnabled();
            UE_LOG(LogTemp, Log, TEXT("Gaze.Enabled=%s"), bNowEnabled ? TEXT("true") : TEXT("false"));
        }
    })
);

static FAutoConsoleCommand GazeValidateStage1Command(
    TEXT("Gaze.ValidateStage1"),
    TEXT("Generate Stage-1 provider artifacts"),
    FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
    {
        if (UGazeProviderSubsystem* Subsystem = ResolveSubsystemFromWorld(Args))
        {
            const bool bOk = Subsystem->WriteStage1Artifacts();
            UE_LOG(LogTemp, Log, TEXT("Gaze.ValidateStage1=%s"), bOk ? TEXT("ok") : TEXT("failed"));
        }
    })
);

} // namespace

void UGazeProviderSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    const UGazeProviderSettings* Settings = GetDefault<UGazeProviderSettings>();
    bEnabled = Settings != nullptr ? Settings->bGazeEnabled : true;
    ProviderName = Settings != nullptr ? Settings->GazeProvider : TEXT("Null");
    ConfidenceThreshold = Settings != nullptr ? FMath::Clamp(Settings->ConfidenceThreshold, 0.0f, 1.0f) : 0.60f;

    ActiveProvider = BuildProvider(ProviderName);
    if (ActiveProvider == nullptr)
    {
        ProviderName = TEXT("Null");
        ActiveProvider = BuildProvider(ProviderName);
    }
}

void UGazeProviderSubsystem::Deinitialize()
{
    ActiveProvider = nullptr;
    Super::Deinitialize();
}

bool UGazeProviderSubsystem::IsEnabled() const
{
    return bEnabled;
}

void UGazeProviderSubsystem::SetEnabled(bool bInEnabled)
{
    bEnabled = bInEnabled;
}

bool UGazeProviderSubsystem::ToggleEnabled()
{
    bEnabled = !bEnabled;
    return bEnabled;
}

FString UGazeProviderSubsystem::GetSelectedProvider() const
{
    return ProviderName;
}

bool UGazeProviderSubsystem::SetProvider(const FString& InProvider)
{
    UObject* NewProvider = BuildProvider(InProvider);
    if (NewProvider == nullptr)
    {
        return false;
    }

    ProviderName = InProvider;
    ActiveProvider = NewProvider;
    return true;
}

FGazeSampleNormalized UGazeProviderSubsystem::GetGatedSample() const
{
    if (!bEnabled)
    {
        return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Null, GetMonotonicNow());
    }

    if (ActiveProvider == nullptr)
    {
        return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Null, GetMonotonicNow());
    }

    if (!ActiveProvider->GetClass()->ImplementsInterface(UGazeProviderInterface::StaticClass()))
    {
        return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Null, GetMonotonicNow());
    }

    const FGazeSampleNormalized RawSample = IGazeProviderInterface::Execute_GetLatestSample(ActiveProvider);
    return ApplyConfidenceGate(RawSample);
}

bool UGazeProviderSubsystem::WriteStage1Artifacts() const
{
    const FString RepoRelative = FPaths::Combine(FPaths::ProjectDir(), TEXT(".."), TEXT(".."), TEXT("solutions"), TEXT("game"), TEXT("fps-gaze-prototype"), TEXT("artifacts"), TEXT("stage-1"));
    const FString ArtifactsDir = FPaths::ConvertRelativePathToFull(RepoRelative);
    IFileManager::Get().MakeDirectory(*ArtifactsDir, true);

    const FGazeSampleNormalized Sample = GetGatedSample();

    const FString RuntimeLogPath = FPaths::Combine(ArtifactsDir, TEXT("runtime_validation.log"));
    const FString SignalContractPath = FPaths::Combine(ArtifactsDir, TEXT("signal_contract.md"));
    const FString ProviderStatusPath = FPaths::Combine(ArtifactsDir, TEXT("provider_status.json"));

    const FString RuntimeLog = FString::Printf(
        TEXT("STAGE1_VALIDATION deterministic\n")
        TEXT("enabled=%s\n")
        TEXT("provider_requested=%s\n")
        TEXT("threshold=%.2f\n")
        TEXT("gating_result=%s\n")
        TEXT("timestamp_semantics=monotonic\n"),
        bEnabled ? TEXT("true") : TEXT("false"),
        *ProviderName,
        ConfidenceThreshold,
        Sample.present ? TEXT("pass") : TEXT("suppressed")
    );

    const FString SignalContract = TEXT("# Stage-1 Normalized Signal Contract\n")
        TEXT("\n")
        TEXT("- gaze_x: float [0,1]\n")
        TEXT("- gaze_y: float [0,1]\n")
        TEXT("- confidence: float [0,1]\n")
        TEXT("- present: bool\n")
        TEXT("- source: enum Tobii|Null\n")
        TEXT("- timestamp: monotonic\n");

    TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("schema_version"), TEXT("stage-1.v1"));
    Root->SetBoolField(TEXT("enabled"), bEnabled);
    Root->SetStringField(TEXT("provider"), ProviderName);
    Root->SetStringField(TEXT("source"), Sample.source == EGazeProviderSource::Tobii ? TEXT("Tobii") : TEXT("Null"));
    Root->SetNumberField(TEXT("threshold"), ConfidenceThreshold);

    TSharedRef<FJsonObject> Shape = MakeShared<FJsonObject>();
    Shape->SetStringField(TEXT("gaze_x"), TEXT("float(0..1)"));
    Shape->SetStringField(TEXT("gaze_y"), TEXT("float(0..1)"));
    Shape->SetStringField(TEXT("confidence"), TEXT("float(0..1)"));
    Shape->SetStringField(TEXT("present"), TEXT("bool"));
    Shape->SetStringField(TEXT("source"), TEXT("enum(Tobii|Null)"));
    Shape->SetStringField(TEXT("timestamp"), TEXT("monotonic"));
    Root->SetObjectField(TEXT("sample_shape"), Shape);

    FString JsonText;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonText);
    const bool bJsonOk = FJsonSerializer::Serialize(Root, Writer);

    const bool bA = FFileHelper::SaveStringToFile(RuntimeLog, *RuntimeLogPath);
    const bool bB = FFileHelper::SaveStringToFile(SignalContract, *SignalContractPath);
    const bool bC = bJsonOk && FFileHelper::SaveStringToFile(JsonText + TEXT("\n"), *ProviderStatusPath);
    return bA && bB && bC;
}

UObject* UGazeProviderSubsystem::BuildProvider(const FString& InProviderName) const
{
    if (InProviderName.Equals(TEXT("Tobii"), ESearchCase::IgnoreCase))
    {
        UObject* Candidate = NewObject<UTobiiGazeProvider>(const_cast<UGazeProviderSubsystem*>(this));
        if (Candidate != nullptr && Candidate->GetClass()->ImplementsInterface(UGazeProviderInterface::StaticClass()))
        {
            const bool bIsAvailable = IGazeProviderInterface::Execute_IsAvailable(Candidate);
            if (bIsAvailable)
            {
                return Candidate;
            }
        }
    }

    return NewObject<UNullGazeProvider>(const_cast<UGazeProviderSubsystem*>(this));
}

FGazeSampleNormalized UGazeProviderSubsystem::ApplyConfidenceGate(const FGazeSampleNormalized& RawSample) const
{
    if (!RawSample.present || RawSample.confidence < ConfidenceThreshold)
    {
        return FGazeSampleNormalized::MakeNoGaze(RawSample.source, RawSample.timestamp);
    }

    FGazeSampleNormalized Clamped = RawSample;
    Clamped.gaze_x = FMath::Clamp(Clamped.gaze_x, 0.0f, 1.0f);
    Clamped.gaze_y = FMath::Clamp(Clamped.gaze_y, 0.0f, 1.0f);
    Clamped.confidence = FMath::Clamp(Clamped.confidence, 0.0f, 1.0f);
    return Clamped;
}

double UGazeProviderSubsystem::GetMonotonicNow() const
{
    return FPlatformTime::Seconds();
}
