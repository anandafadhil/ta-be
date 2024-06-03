from locust import HttpUser, TaskSet, task, between

# class UserBehavior(TaskSet):
class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
    wait_time = between(1, 5)

    @task
    def selector(self):
        self.client.get("/univ-predict")
        self.client.get("/prodi-predict/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/univ-vis")
        self.client.get("/prodi-vis/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/select-year")

    @task
    def predict(self):
        self.client.post("/predict", json={
            "IPK_sem_1": "4",
            "IPK_sem_2": "4",
            "IPK_sem_3": "4",
            "IPK_sem_4": "4",
            "SKS_sem_1": "18",
            "SKS_sem_2": "18",
            "SKS_sem_3": "18",
            "SKS_sem_4": "18",
            "SKSL_sem_1": "18",
            "SKSL_sem_2": "18",
            "SKSL_sem_3": "18",
            "SKSL_sem_4": "18",
            "id": "DD1A434D-056F-4A0F-8979-3FF77D380352"
        })

    @task
    def predict_bulk(self):
        self.client.post("/predict-bulk", json={
            "data": [
                {
                "NPM": "2006411111",
                "IPK_sem_1": "2",
                "IPK_sem_2": "2",
                "IPK_sem_3": "3",
                "IPK_sem_4": "2",
                "SKS_sem_1": "18",
                "SKS_sem_2": "18",
                "SKS_sem_3": "18",
                "SKS_sem_4": "18",
                "SKSL_sem_1": "18",
                "SKSL_sem_2": "18",
                "SKSL_sem_3": "18",
                "SKSL_sem_4": "18"
                },
                {
                    "NPM": "2006422222",
                    "IPK_sem_1": "4",
                    "IPK_sem_2": "4",
                    "IPK_sem_3": "4",
                    "IPK_sem_4": "4",
                    "SKS_sem_1": "18",
                    "SKS_sem_2": "18",
                    "SKS_sem_3": "18",
                    "SKS_sem_4": "18",
                    "SKSL_sem_1": "18",
                    "SKSL_sem_2": "18",
                    "SKSL_sem_3": "18",
                    "SKSL_sem_4": "18"
                },
                {
                    "NPM": "2006433333",
                    "IPK_sem_1": "3.7",
                    "IPK_sem_2": "3.5",
                    "IPK_sem_3": "3.2",
                    "IPK_sem_4": "3",
                    "SKS_sem_1": "18",
                    "SKS_sem_2": "20",
                    "SKS_sem_3": "20",
                    "SKS_sem_4": "20",
                    "SKSL_sem_1": "18",
                    "SKSL_sem_2": "20",
                    "SKSL_sem_3": "20",
                    "SKSL_sem_4": "20"
                }
            ],
            "id": "D5D36093-9656-43FE-BFCC-C1ED1873EECB"
        })
        
    @task
    def get_ipk_total(self):
        self.client.post("/total-ipk", json={
    "IPK_sem_1": "4",  
    "IPK_sem_2": "4", 
    "IPK_sem_3": "4", 
    "IPK_sem_4": "4", 
    "id": "DD1A434D-056F-4A0F-8979-3FF77D380352"
}
)
    @task
    def get_sks_total(self):
        self.client.post("/total-sks", json={
    "SKSL_sem_1": "18", 
    "SKSL_sem_2": "18", 
    "SKSL_sem_3": "18", 
    "SKSL_sem_4": "18", 
    "id": "DD1A434D-056F-4A0F-8979-3FF77D380352"
}

)
    @task
    def get_sks_needed(self):
        self.client.post("/sks-needed", json={
    "SKSL_sem_1": "18", 
    "SKSL_sem_2": "18", 
    "SKSL_sem_3": "18", 
    "SKSL_sem_4": "18", 
    "id": "DD1A434D-056F-4A0F-8979-3FF77D380352"
}

)
    @task
    def handle_table_bulk(self):
        self.client.post("/handle-table-bulk", json={
    "data": [
        {
            "NPM": "333",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "222",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "333",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "444",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "555",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "666",
            "RES": "Tidak Tepat Waktu"
        },
        {
            "NPM": "777",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "888",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "999",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "10",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "11",
            "RES": "Tepat Waktu"
        },
        {
            "NPM": "12",
            "RES": "Tepat Waktu"
        }
    ],
    "pageSize": 5,
    "pageNumber": 1
}
)


    @task
    def all_stat(self):
        self.client.get("/total-univ")
        self.client.get("/total-prodi")
        self.client.get("/average-grad-time")
        self.client.get("/grad-timeliness")
        self.client.get("/grad-progression")
        self.client.get("/grad-distribution/All")
        self.client.get("/geochart/All")

    @task
    def univ(self):
        self.client.get("/univ-information/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/average-grad-time-univ/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/prodi-ranking/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/grad-time-distribution-univ/0D1E63E9-CBFB-4546-A242-875C310083A5/All")
        self.client.get("/grad-timeliness-univ/0D1E63E9-CBFB-4546-A242-875C310083A5")
        self.client.get("/grad-progression-univ/0D1E63E9-CBFB-4546-A242-875C310083A5")

    @task
    def prodi(self):
        self.client.get("/prodi-information/D5D36093-9656-43FE-BFCC-C1ED1873EECB")
        self.client.get("/avg-ipk/E9CB9676-746D-4FB0-859F-26B105D13672")
        self.client.get("/avg-sks/C364E6A3-BB6E-4003-9123-000498EE03E3")
        self.client.get("/average-grad-time-prodi/D5D36093-9656-43FE-BFCC-C1ED1873EECB")
        self.client.get("/grad-timeliness-prodi/D5D36093-9656-43FE-BFCC-C1ED1873EECB")
        self.client.get("/grad-progression-prodi/D5D36093-9656-43FE-BFCC-C1ED1873EECB")
        self.client.get("/grad-time-distribution-prodi/D5D36093-9656-43FE-BFCC-C1ED1873EECB/All")


# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     wait_time = between(1, 5)
