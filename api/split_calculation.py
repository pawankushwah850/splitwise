from django.db.models import F

from split.models import SplitAmountToUser, User


def split_calculation(borrow_by: User, split_owner: User, amount: float) -> None:
    # condition need to check, if split owner borrow amount from this user before
    instance = SplitAmountToUser.objects.filter(borrow_from=borrow_by, borrow_by=split_owner, amount__gte=1)
    if instance.exists():
        # Now check how much split owner borrow amount before
        instance = instance.first()
        if instance.amount > amount:
            instance.amount = F("amount") - amount
            instance.save(update_fields=("amount",))
        else:
            amount = float(amount) - float(instance.amount)

            # update balance or create split amount
            obj = SplitAmountToUser.objects.filter(borrow_from=split_owner, borrow_by=borrow_by)
            if obj.exists():
                obj.update(amount=amount)
            else:
                SplitAmountToUser.objects.create(borrow_from=split_owner, borrow_by=borrow_by, amount=amount)

            # update balance 0 if not borrow amount is pending
            SplitAmountToUser.objects.filter(borrow_from=borrow_by, borrow_by=split_owner).update(amount=0)
    else:
        # now check if split owner again giving money to same user then add amount
        # Other wise create split amount

        ins = SplitAmountToUser.objects.filter(borrow_from=split_owner, borrow_by=borrow_by)
        if ins.exists():
            ins.update(amount=F("amount") + amount)
        else:
            SplitAmountToUser.objects.create(borrow_from=split_owner, borrow_by=borrow_by, amount=amount)
