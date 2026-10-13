from fastapi import Depends,FastAPI


router = FastAPI()


def common_params(
    page: int = 1,
    size: int = 10,
):
    return {
        "page": page,
        "size": size,
    }


@router.get("/")
def get_users(
    params: dict = Depends(common_params)
):
    return params




