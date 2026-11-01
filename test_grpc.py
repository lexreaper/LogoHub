
import grpc

import recommendation_pb2
import recommendation_pb2_grpc


def main():
    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        client = recommendation_pb2_grpc.RecommendationServiceStub(
            channel
        )

        request = recommendation_pb2.RecommendRequest(
            specialization_id=2,
            therapists=[
                recommendation_pb2.Therapist(
                    id=1,
                    specialization_ids=[1, 2],
                    experience_years=5
                ),
                recommendation_pb2.Therapist(
                    id=2,
                    specialization_ids=[2, 3],
                    experience_years=10
                ),
                recommendation_pb2.Therapist(
                    id=3,
                    specialization_ids=[1, 3],
                    experience_years=15
                )
            ]
        )

        response = client.Recommend(request, timeout=5)

        print("Рекомендованные логопеды:")
        print(list(response.therapist_ids))

        assert list(response.therapist_ids) == [2, 1]
        print("Тест успешно пройден!")


if __name__ == "__main__":
    main()
